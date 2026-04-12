from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.events import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, event: Event) -> Event:
        result = await self._session.execute(select(Event).where(Event.id == event.id))
        existing_event = result.scalar_one_or_none()

        if existing_event is None:
            self._session.add(event)
            await self._session.commit()
            await self._session.refresh(event)
            return event

        existing_event.place_id = event.place_id
        existing_event.name = event.name
        existing_event.event_time = event.event_time
        existing_event.registration_deadline = event.registration_deadline
        existing_event.status = event.status
        existing_event.number_of_visitors = event.number_of_visitors
        existing_event.changed_at = event.changed_at
        existing_event.created_at = event.created_at
        existing_event.status_changed_at = event.status_changed_at

        await self._session.commit()
        await self._session.refresh(existing_event)
        return existing_event
