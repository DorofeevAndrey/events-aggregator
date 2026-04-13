from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.service.events import EventsService
from src.application.service.seats import SeatsService
from src.core.config import get_settings
from src.db.session import get_db_session
from src.infrastructure.events_provider.client import EventsProviderClient
from src.repositories.event_repository import EventRepository
from src.schemas.events.event_query import EventQuerySchema
from src.schemas.events.events import (
    EventDetailSchema,
    EventListResponseSchema,
    EventSeatsResponseSchema,
)

router = APIRouter()


@router.get("/events", response_model=EventListResponseSchema)
async def list_events(
    request: Request,
    params: EventQuerySchema = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    service = EventsService(EventRepository(session=session))
    return await service.list_events(
        request=request,
        date_from=params.date_from,
        page=params.page,
        page_size=params.page_size,
    )


@router.get("/events/{event_id}", response_model=EventDetailSchema)
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_db_session)):
    service = EventsService(EventRepository(session=session))
    return await service.get_event(event_id=event_id)


@router.get("/events/{event_id}/seats", response_model=EventSeatsResponseSchema)
async def get_seats(event_id: UUID, session: AsyncSession = Depends(get_db_session)):
    settings = get_settings()

    async with EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key,
    ) as client:
        service = SeatsService(
            client=client,
            events_repository=EventRepository(session=session),
        )
        return await service.get_seats(event_id=event_id)
