from time import monotonic
from uuid import UUID

from fastapi import HTTPException

from src.application.ports.events import (
    EventRepositoryPort,
    EventsProviderSeatsClientPort,
)

_SEATS_CACHE: dict[UUID, tuple[float, list[str]]] = {}
_SEATS_CACHE_TTL_SECONDS = 30.0


class SeatsService:
    def __init__(
        self,
        client: EventsProviderSeatsClientPort,
        events_repository: EventRepositoryPort,
    ):
        self._client = client
        self._events_repository = events_repository

    async def get_seats(self, event_id: UUID) -> dict[str, list[str]]:
        event = await self._events_repository.get_by_id(event_id=event_id)

        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(
                status_code=400,
                detail="Event is not published",
            )

        cached = _SEATS_CACHE.get(event_id)
        now = monotonic()
        if cached is not None and now - cached[0] < _SEATS_CACHE_TTL_SECONDS:
            return {"seats": cached[1]}

        response = await self._client.seats(event_id=event_id)
        seats = sorted(response["seats"])
        _SEATS_CACHE[event_id] = (now, seats)

        return {"seats": seats}
