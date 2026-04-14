from pydantic import BaseModel


class TicketDeleteResponseSchema(BaseModel):
    success: bool
