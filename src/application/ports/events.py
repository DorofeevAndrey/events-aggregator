from datetime import date
from typing import Any, Protocol
from uuid import UUID

from src.db.models.events import Event


class EventRepositoryPort(Protocol):
    async def count(self, date_from: date | None) -> int: ...

    async def list(
        self, date_from: date | None = None, offset: int = 0, limit: int = 20
    ) -> list[Event]: ...

    async def get_by_id(self, event_id: UUID) -> Event | None: ...


class EventsProviderSeatsClientPort(Protocol):
    async def seats(self, event_id: str) -> dict[str, Any]: ...
