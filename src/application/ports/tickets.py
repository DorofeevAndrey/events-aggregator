from typing import Protocol
from uuid import UUID


class EventsProviderClientPort(Protocol):
    async def create_ticket(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, str]: ...

    async def seats(self, event_id: UUID) -> dict: ...
