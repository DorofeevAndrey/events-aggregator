from pydantic import BaseModel


class TicketResponseSchema(BaseModel):
    ticket_id: str
