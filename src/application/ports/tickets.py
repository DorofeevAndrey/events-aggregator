from typing import Protocol
from uuid import UUID

from src.db.models.tickets import Ticket


class EventProviderClientPort(Protocol):
    async def create_ticket(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, str]: ...

    async def seats(self, event_id: UUID) -> dict: ...


class TicketRepositoryPort(Protocol):
    async def get_by_email(self, email: str) -> Ticket | None: ...

    async def create(self, ticket: Ticket) -> Ticket: ...
