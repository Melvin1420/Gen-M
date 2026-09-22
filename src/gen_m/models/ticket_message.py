from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING 

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gen_m.database.base import Base

if TYPE_CHECKING:
    from gen_m.models.ticket import Ticket
    from gen_m.models.user import User

class TicketMessage(Base):
    """One message in a ticket's chat thread between requester and agent."""

    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<TicketMessage(id={self.id}, ticket_id={self.ticket_id}, sender_id={self.sender_id})>"

    
