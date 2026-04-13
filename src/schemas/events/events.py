from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlaceListSchema(BaseModel):
    id: UUID
    name: str
    city: str
    address: str

    model_config = ConfigDict(from_attributes=True)


class PlaceDetailSchema(PlaceListSchema):
    seats_pattern: str


class EventListSchema(BaseModel):
    id: UUID
    name: str
    place: PlaceListSchema
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int

    model_config = ConfigDict(from_attributes=True)


class EventDetailSchema(EventListSchema):
    place: PlaceDetailSchema


class EventListResponseSchema(BaseModel):
    count: int
    next: str | None
    previous: str | None
    results: list[EventListSchema]


class EventSeatsResponseSchema(BaseModel):
    event_id: str
    available_seats: list[str]
