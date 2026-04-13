from datetime import date
from typing import Protocol

from src.db.models.events import Event


class EventRepositoryPort(Protocol):
    async def count(self, date_from: date | None) -> int: ...

    async def list(
        self, date_from: date | None = None, offset: int = 0, limit: int = 20
    ) -> list[Event]: ...
