from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING 

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gen_m.database.base import Base

if TYPE_CHECKING:
    from gen_m.models.asset import Asset
    from gen_m.models.department import Department
    from gen_m.models.ticket_message import TicketMessage 
    from gen_m.models.user import User

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Ticket(Base):
    """A Support Ticket, auto-routed to a department queue by category"""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, native_enum=True), nullable=False, default=TicketStatus.OPEN
    )
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority, native_enum=True), nullable=False, default=TicketPriority.MEDIUM
    )

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_agent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), nullable=False)
    asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    requester: Mapped["User"] = relationship(
        back_populates="tickets_requested", foreign_keys=[requester_id]
    )
    assigned_agent: Mapped["User | None"] = relationship(
        back_populates="tickets_assigned", foreign_keys=[assigned_agent_id]
    )
    department: Mapped["Department"] = relationship(back_populates="tickets")
    asset: Mapped["Asset | None"] = relationship(back_populates="tickets")
    messages: Mapped[list["TicketMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at"
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} status={self.status.value} priority={self.priority.value}>"

