from urllib.parse import parse_qs, urlparse

from src.infrastructure.events_provider.client import EventsProviderClient
from src.schemas.provider.provider_event import ProviderEventSchema
from src.schemas.provider.provider_events_page import ProviderEventsPageSchema


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str):
        self._client = client
        self._changed_at = changed_at
        self._cursor: str | None = None
        self._buffer: list[ProviderEventSchema] = []

    def __aiter__(self):
        return self

    async def __anext__(self) -> ProviderEventSchema:
        while not self._buffer:
            page_data = await self._client.events(
                changed_at=self._changed_at,
                cursor=self._cursor,
            )
            page = ProviderEventsPageSchema.model_validate(page_data)

            self._cursor = self._extract_cursor(page.next)
            self._buffer = page.results

            if not self._buffer and self._cursor is None:
                raise StopAsyncIteration

        return self._buffer.pop(0)

    def _extract_cursor(self, next_url: str | None) -> str | None:
        if not next_url:
            return None

        parsed = urlparse(next_url)
        return parse_qs(parsed.query).get("cursor", [None])[0]
