from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TicketRequestSchema(BaseModel):
    event_id: UUID
    first_name: str = Field(..., min_length=1, description="First name cannot be empty")
    last_name: str = Field(..., min_length=1, description="Last name cannot be empty")
    email: EmailStr
    seat: str = Field(
        ...,
        pattern=r"^[A-Z]\d{1,3}$",
        description="Seat format like A1, B15, C100",
        examples=["A1", "B12"],
    )
