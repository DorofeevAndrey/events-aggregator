from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.service.tickets import TicketsService
from src.core.config import get_settings
from src.db.session import get_db_session
from src.infrastructure.events_provider.client import EventsProviderClient
from src.repositories.event_repository import EventRepository
from src.repositories.ticket_repository import TicketRepository
from src.schemas.tickets.ticket_request import TicketRequestSchema
from src.schemas.tickets.ticket_response import TicketResponseSchema

router = APIRouter()


@router.post("/tickets", response_model=TicketResponseSchema, status_code=201)
async def create_ticket(
    params: TicketRequestSchema, session: AsyncSession = Depends(get_db_session)
):
    settings = get_settings()

    async with EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key,
    ) as client:
        service = TicketsService(
            client=client,
            event_repository=EventRepository(session=session),
            ticket_repository=TicketRepository(session=session),
        )
        return await service.create_ticket(
            event_id=params.event_id,
            first_name=params.first_name,
            last_name=params.last_name,
            email=params.email,
            seat=params.seat,
        )
