from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus

class TicketBase(BaseModel):
    requester_name: str = Field(
        min_length=2,
        max_length=150,
    )

    subject: str = Field(
        min_length=2,
        max_length=255,
    )

    description: str = Field(
        min_length=3,
        max_length=5000,
    )

    priority: TicketPriority = TicketPriority.medium

class TicketCreate(TicketBase):
    pass

class TicketResponse(BaseModel):
    ticket_id: int
    ticket_number: str
    requester_name: str
    subject: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)