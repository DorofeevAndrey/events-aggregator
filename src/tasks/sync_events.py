import asyncio
import logging

from src.application.service.sync_events import SyncEventsService
from src.core.config import get_settings
from src.db.session import AsyncSessionLocal
from src.infrastructure.events_provider.client import EventsProviderClient
from src.repositories.event_repository import EventRepository
from src.repositories.place_repository import PlaceRepository
from src.repositories.sync_state_repository import SyncStateRepository

logger = logging.getLogger(__name__)


async def sync_events():
    settings = get_settings()
    async with EventsProviderClient(
        base_url=settings.events_provider_base_url,
        api_key=settings.events_provider_api_key,
    ) as client:
        async with AsyncSessionLocal() as session:
            service = SyncEventsService(
                client=client,
                place_repository=PlaceRepository(session),
                event_repository=EventRepository(session),
                sync_state_repository=SyncStateRepository(session),
            )

            await service.sync()


async def background_sync() -> None:
    while True:
        logger.info("Background sync started")

        try:
            await sync_events()
            logger.info("Background sync completed")
        except asyncio.CancelledError:
            logger.info("Background sync cancelled")
            raise
        except Exception:
            logger.exception("Background sync failed")

        logger.info("Sleeping for 24h")
        await asyncio.sleep(24 * 60 * 60)
