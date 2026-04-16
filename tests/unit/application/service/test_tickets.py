from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest

from src.application.exceptions import (
    CannotCancelAfterEventPassedError,
    EmailAlreadyRegisteredError,
    EventNotPublishedError,
    RegistrationClosedError,
    SeatUnavailableError,
)
from src.application.service.tickets import TicketsService
from src.db.models.tickets import Ticket
from src.schemas.events.event_status import EventStatus

EVENT_ID = UUID("550e8400-e29b-41d4-a716-446655440000")
TICKET_ID = UUID("1fed0122-b675-42e2-8ae7-49bfb53e8d7f")


@pytest.fixture()
def ticket_service():
    client = Mock()
    client.seats = AsyncMock()
    client.create_ticket = AsyncMock()
    client.delete_ticket = AsyncMock()

    event_repository = Mock()
    event_repository.get_by_id = AsyncMock()

    ticket_repository = Mock()
    ticket_repository.get_by_event_and_email = AsyncMock()
    ticket_repository.get_by_provider_ticket_id = AsyncMock()
    ticket_repository.create = AsyncMock()
    ticket_repository.delete_by_provider_ticket_id = AsyncMock()

    service = TicketsService(
        client=client,
        event_repository=event_repository,
        ticket_repository=ticket_repository,
    )

    return SimpleNamespace(
        service=service,
        client=client,
        event_repository=event_repository,
        ticket_repository=ticket_repository,
    )


def make_event(
    *, status=EventStatus.PUBLISHED, event_time=None, registration_deadline=None
):
    return SimpleNamespace(
        status=status,
        event_time=event_time or (datetime.now(UTC) + timedelta(days=1)),
        registration_deadline=registration_deadline
        or (datetime.now(UTC) + timedelta(days=1)),
    )


def make_ticket(provider_ticket_id: UUID = TICKET_ID):
    return SimpleNamespace(
        event_id=EVENT_ID,
        provider_ticket_id=provider_ticket_id,
    )


@pytest.mark.asyncio
async def test_create_ticket_success(ticket_service):
    ticket_service.event_repository.get_by_id.return_value = make_event()
    ticket_service.ticket_repository.get_by_event_and_email.return_value = None
    ticket_service.client.seats.return_value = {"seats": ["A15", "A16"]}
    ticket_service.client.create_ticket.return_value = {"ticket_id": str(TICKET_ID)}

    response = await ticket_service.service.create_ticket(
        event_id=EVENT_ID,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A15",
    )

    assert response == {"ticket_id": str(TICKET_ID)}
    ticket_service.event_repository.get_by_id.assert_awaited_once_with(
        event_id=EVENT_ID
    )
    ticket_service.ticket_repository.get_by_event_and_email.assert_awaited_once_with(
        event_id=EVENT_ID,
        email="ivan@example.com",
    )
    ticket_service.client.seats.assert_awaited_once_with(EVENT_ID)
    ticket_service.client.create_ticket.assert_awaited_once_with(
        event_id=EVENT_ID,
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@example.com",
        seat="A15",
    )
    ticket_service.ticket_repository.create.assert_awaited_once()
    created_ticket = ticket_service.ticket_repository.create.await_args.args[0]
    assert isinstance(created_ticket, Ticket)
    assert created_ticket.event_id == EVENT_ID
    assert created_ticket.provider_ticket_id == TICKET_ID
    assert created_ticket.email == "ivan@example.com"
    assert created_ticket.seat == "A15"


@pytest.mark.asyncio
async def test_create_ticket_rejects_unpublished_event(ticket_service):
    ticket_service.event_repository.get_by_id.return_value = make_event(
        status=EventStatus.DRAFT
    )

    with pytest.raises(EventNotPublishedError):
        await ticket_service.service.create_ticket(
            event_id=EVENT_ID,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A15",
        )

    ticket_service.client.seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_ticket_rejects_closed_registration(ticket_service):
    ticket_service.event_repository.get_by_id.return_value = make_event(
        registration_deadline=datetime(2000, 1, 1, tzinfo=UTC)
    )

    with pytest.raises(RegistrationClosedError):
        await ticket_service.service.create_ticket(
            event_id=EVENT_ID,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A15",
        )

    ticket_service.client.seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_ticket_rejects_already_registered_email(ticket_service):
    ticket_service.event_repository.get_by_id.return_value = make_event()
    ticket_service.ticket_repository.get_by_event_and_email.return_value = make_ticket()

    with pytest.raises(EmailAlreadyRegisteredError):
        await ticket_service.service.create_ticket(
            event_id=EVENT_ID,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A15",
        )

    ticket_service.client.seats.assert_not_awaited()
    ticket_service.client.create_ticket.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_ticket_rejects_unavailable_seat(ticket_service):
    ticket_service.event_repository.get_by_id.return_value = make_event()
    ticket_service.ticket_repository.get_by_event_and_email.return_value = None
    ticket_service.client.seats.return_value = {"seats": ["A16"]}

    with pytest.raises(SeatUnavailableError):
        await ticket_service.service.create_ticket(
            event_id=EVENT_ID,
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A15",
        )

    ticket_service.client.create_ticket.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_ticket_success(ticket_service):
    ticket_service.ticket_repository.get_by_provider_ticket_id.return_value = (
        make_ticket()
    )
    ticket_service.event_repository.get_by_id.return_value = make_event(
        event_time=datetime.now(UTC) + timedelta(days=1)
    )
    ticket_service.client.delete_ticket.return_value = {"success": True}

    response = await ticket_service.service.delete_ticket(ticket_id=TICKET_ID)

    assert response == {"success": True}
    ticket_service.client.delete_ticket.assert_awaited_once_with(
        event_id=EVENT_ID,
        ticket_id=TICKET_ID,
    )
    ticket_service.ticket_repository.delete_by_provider_ticket_id.assert_awaited_once_with(
        ticket_id=TICKET_ID
    )


@pytest.mark.asyncio
async def test_delete_ticket_rejects_past_event(ticket_service):
    ticket_service.ticket_repository.get_by_provider_ticket_id.return_value = (
        make_ticket()
    )
    ticket_service.event_repository.get_by_id.return_value = make_event(
        event_time=datetime(2000, 1, 1, tzinfo=UTC)
    )

    with pytest.raises(CannotCancelAfterEventPassedError):
        await ticket_service.service.delete_ticket(ticket_id=TICKET_ID)

    ticket_service.client.delete_ticket.assert_not_awaited()
