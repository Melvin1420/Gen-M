from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from gen_m.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    title: str
    description: str
    category: str
    department_id: int
    priority: TicketPriority = TicketPriority.MEDIUM
    asset_id: int | None = None


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None
    department_id: int | None = None
    assigned_agent_id: int | None = None
    asset_id: int | None = None


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: str
    status: TicketStatus
    priority: TicketPriority
    requester_id: int
    assigned_agent_id: int | None
    department_id: int
    asset_id: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class TicketMessageCreate(BaseModel):
    message: str


class TicketMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    sender_id: int
    message: str
    created_at: datetime
