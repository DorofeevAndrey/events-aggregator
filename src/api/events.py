from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.event_repository import EventRepository
from src.application.service.events import EventsService
from src.schemas.events.event_query import EventQuerySchema
from src.schemas.events.events import EventListResponseSchema
from src.db.session import get_db_session


router = APIRouter()


@router.get("/events", response_model=EventListResponseSchema)
async def list_events(
    request: Request,
    params: EventQuerySchema = Depends(),
    session: AsyncSession = Depends(get_db_session),
):
    service = EventsService(EventRepository(session))
    return await service.list_events(
        request=request,
        date_from=params.date_from,
        page=params.page,
        page_size=params.page_size,
    )
