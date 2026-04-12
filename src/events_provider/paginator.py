from collections.abc import AsyncIterator
from typing import Any

from src.events_provider.client import EventsProviderClient


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str):
        self._client = client
        self._changed_at = changed_at
        self._cursor: str | None = None
        self._buffer: list[dict[str, Any]] = []

    def __aiter__(self):
        return self

    async def __anext__(self) -> dict[str, Any]:
        while not self._buffer:
            page = await self._client.events(
                changed_at=self._changed_at,
                cursor=self._cursor,
            )

            self._cursor = page["next"]
            self._buffer = page["results"]

            if not self._buffer and self._cursor is None:
                raise StopAsyncIteration

        return self._buffer.pop(0)
