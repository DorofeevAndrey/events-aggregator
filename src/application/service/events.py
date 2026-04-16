from datetime import date
from uuid import UUID

from fastapi import Request

from src.application.exceptions import EventNotFoundError
from src.application.ports.events import EventRepositoryPort


class EventsService:
    def __init__(self, events_repository: EventRepositoryPort):
        self._event_repository = events_repository

    async def list_events(
        self, request: Request, date_from: date | None, page: int, page_size: int
    ):
        offset = (page - 1) * page_size
        count = await self._event_repository.count(date_from=date_from)
        events = await self._event_repository.list(
            date_from=date_from, offset=offset, limit=page_size
        )

        next_url = None
        if offset + page_size < count:
            next_url = str(
                request.url.include_query_params(
                    page=page + 1,
                    page_size=page_size,
                    date_from=date_from.isoformat() if date_from else None,
                )
            )

        previous_url = None
        if page > 1:
            previous_url = str(
                request.url.include_query_params(
                    page=page - 1,
                    page_size=page_size,
                    date_from=date_from.isoformat() if date_from else None,
                )
            )

        return {
            "count": count,
            "next": next_url,
            "previous": previous_url,
            "results": events,
        }

    async def get_event(self, event_id: UUID):
        event = await self._event_repository.get_by_id(event_id=event_id)

        if not event:
            raise EventNotFoundError()

        return event
