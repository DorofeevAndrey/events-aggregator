from collections.abc import AsyncIterator
from typing import Any, Protocol

from src.db.models.events import Event
from src.db.models.places import Place
from src.db.models.sync_state import SyncState
from src.schemas.provider.provider_event import ProviderEventSchema


class EventsProviderClientPort(Protocol):
    async def events(
        self,
        changed_at: str,
        cursor: str | None = None,
    ) -> dict[str, Any]: ...


class PlaceRepositoryPort(Protocol):
    async def upsert(self, place: Place) -> Place: ...


class EventRepositoryPort(Protocol):
    async def upsert(self, event: Event) -> Event: ...


class SyncStateRepositoryPort(Protocol):
    async def get_or_create(self) -> SyncState: ...

    async def mark_running(self) -> SyncState: ...

    async def mark_success(self, last_changed_at) -> SyncState: ...

    async def mark_failed(self, error_message: str) -> SyncState: ...


class EventsPaginatorPort(Protocol):
    def __aiter__(self) -> AsyncIterator[ProviderEventSchema]: ...
