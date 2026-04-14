from typing import Protocol
from uuid import UUID

from src.db.models.tickets import Ticket


class EventProviderClientPort(Protocol):
    async def create_ticket(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, str]: ...

    async def delete_ticket(
        self, event_id: UUID, ticket_id: UUID
    ) -> dict[str, str]: ...


class TicketRepositoryPort(Protocol):
    async def get_by_event_and_email(
        self, event_id: UUID, email: str
    ) -> Ticket | None: ...

    async def create(self, ticket: Ticket) -> Ticket: ...

    async def get_by_provider_ticket_id(self, ticket_id: UUID) -> Ticket | None: ...

    async def delete_by_provider_ticket_id(self, ticket_id: UUID) -> bool: ...
