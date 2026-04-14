from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.service.sync_events import SyncEventsService
from src.core.config import get_settings
from src.db.session import get_db_session
from src.infrastructure.events_provider.client import EventsProviderClient
from src.repositories.event_repository import EventRepository
from src.repositories.place_repository import PlaceRepository
from src.repositories.sync_state_repository import SyncStateRepository
from src.infrastructure.events_provider.paginator import EventsPaginator

router = APIRouter()


@router.post("/sync/trigger")
async def sync_trigger(session: AsyncSession = Depends(get_db_session)):
    settings = get_settings()
    async with EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key,
    ) as client:
        service = SyncEventsService(
            client=client,
            client_paginator=EventsPaginator,
            place_repository=PlaceRepository(session),
            event_repository=EventRepository(session),
            sync_state_repository=SyncStateRepository(session),
        )

        await service.sync()

    return {"status": "sync triggered"}
