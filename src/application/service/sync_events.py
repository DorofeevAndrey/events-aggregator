from src.application.mappers.sync_events import build_event_model, build_place_model
from src.application.ports.sync_events import (
    EventRepositoryPort,
    EventsPaginatorPort,
    EventsProviderClientPort,
    PlaceRepositoryPort,
    SyncStateRepositoryPort,
)
from src.infrastructure.events_provider.paginator import EventsPaginator


class SyncEventsService:

    def __init__(
        self,
        client: EventsProviderClientPort,
        place_repository: PlaceRepositoryPort,
        event_repository: EventRepositoryPort,
        sync_state_repository: SyncStateRepositoryPort,
        client_paginator: EventsPaginatorPort,
    ):
        self._client = client
        self._place_repository = place_repository
        self._event_repository = event_repository
        self._sync_state_repository = sync_state_repository
        self._client_paginator = client_paginator

    async def sync(self) -> None:
        sync_state = await self._sync_state_repository.get_or_create()
        changed_at = (
            sync_state.last_changed_at.date().isoformat()
            if sync_state.last_changed_at
            else "2000-01-01"
        )

        try:
            await self._sync_state_repository.mark_running()

            paginator = self._client_paginator(self._client, changed_at=changed_at)

            max_changed_at = sync_state.last_changed_at

            async for provider_event in paginator:
                await self._place_repository.upsert(build_place_model(provider_event))
                await self._event_repository.upsert(build_event_model(provider_event))

                if max_changed_at is None or provider_event.changed_at > max_changed_at:
                    max_changed_at = provider_event.changed_at

            await self._sync_state_repository.mark_success(max_changed_at)

        except Exception as exc:
            await self._sync_state_repository.mark_failed(str(exc))
            raise
