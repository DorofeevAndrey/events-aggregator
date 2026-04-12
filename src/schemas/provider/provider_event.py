from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.schemas.provider.provider_place import ProviderPlaceSchema


class ProviderEventSchema(BaseModel):
    id: UUID
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    changed_at: datetime
    created_at: datetime
    status_changed_at: datetime | None = None

    place: ProviderPlaceSchema
