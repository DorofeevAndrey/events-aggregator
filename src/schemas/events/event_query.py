from datetime import date

from pydantic import BaseModel, Field


class EventQuerySchema(BaseModel):
    date_from: date | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
