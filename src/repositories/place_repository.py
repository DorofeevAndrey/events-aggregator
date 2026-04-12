from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.places import Place


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, place: Place) -> Place:
        result = await self._session.execute(select(Place).where(Place.id == place.id))
        existing_place = result.scalar_one_or_none()

        if existing_place is None:
            self._session.add(place)
            await self._session.commit()
            await self._session.refresh(place)
            return place

        existing_place.name = place.name
        existing_place.city = place.city
        existing_place.address = place.address
        existing_place.seats_pattern = place.seats_pattern
        existing_place.changed_at = place.changed_at
        existing_place.created_at = place.created_at

        await self._session.commit()
        await self._session.refresh(existing_place)
        return existing_place
