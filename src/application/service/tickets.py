from datetime import UTC, datetime
from uuid import UUID

import httpx
from fastapi import HTTPException

from src.application.ports.events import EventRepositoryPort
from src.application.ports.tickets import EventProviderClientPort, TicketRepositoryPort
from src.db.models.tickets import Ticket


class TicketsService:
    def __init__(
        self,
        client: EventProviderClientPort,
        event_repository: EventRepositoryPort,
        ticket_repository: TicketRepositoryPort,
    ):
        self._client = client
        self._event_repository = event_repository
        self._ticket_repository = ticket_repository

    async def create_ticket(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, str]:
        event = await self._event_repository.get_by_id(event_id=event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(status_code=400, detail="Event is not published")

        if event.registration_deadline < datetime.now(UTC):
            raise HTTPException(status_code=400, detail="Registration is closed")

        existing_email = await self._ticket_repository.get_by_event_and_email(
            event_id=event_id,
            email=email,
        )

        if existing_email is not None:
            raise HTTPException(
                status_code=400,
                detail="This email is already registered for this event",
            )

        seats_data = await self._client.seats(event_id)

        available_seats = set(seats_data["seats"])

        if seat not in available_seats:
            raise HTTPException(status_code=400, detail="Seat is unavailable")

        try:
            response = await self._client.create_ticket(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                seat=seat,
            )
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 400:
                raise HTTPException(
                    status_code=400,
                    detail="Seat is unavailable",
                ) from error

            raise

        ticket = Ticket(
            event_id=event_id,
            provider_ticket_id=UUID(response["ticket_id"]),
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            created_at=datetime.now(UTC),
        )
        await self._ticket_repository.create(ticket)

        return response

    async def delete_ticket(self, ticket_id: UUID) -> dict[str, bool]:
        ticket = await self._ticket_repository.get_by_provider_ticket_id(
            ticket_id=ticket_id
        )

        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        if ticket.provider_ticket_id is None:
            raise HTTPException(
                status_code=400, detail="Ticket not synced with provider"
            )

        try:
            response = await self._client.delete_ticket(
                event_id=ticket.event_id,
                ticket_id=ticket.provider_ticket_id,
            )

        except httpx.HTTPStatusError as error:
            if error.response.status_code == 400:
                raise HTTPException(
                    status_code=400,
                    detail="Can't delete ticket",
                ) from error

            raise

        if response.get("success") is not True:
            raise HTTPException(
                status_code=502, detail="Provider did not confirm delete"
            )

        await self._ticket_repository.delete_by_provider_ticket_id(ticket_id=ticket_id)

        return {"success": True}
