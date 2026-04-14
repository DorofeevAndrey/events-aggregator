from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.tickets import Ticket


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_event_and_email(self, event_id: UUID, email: str) -> Ticket | None:
        query = select(Ticket).where(Ticket.event_id == event_id, Ticket.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, ticket: Ticket) -> Ticket:
        self._session.add(ticket)
        await self._session.commit()
        await self._session.refresh(ticket)
        return ticket
