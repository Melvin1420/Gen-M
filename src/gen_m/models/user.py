# src/gen_m/models/user.py
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gen_m.database.base import Base

if TYPE_CHECKING:
    from gen_m.models.department import Department
    from gen_m.models.ticket import Ticket
    from gen_m.models.ticket_message import TicketMessage


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    IT_AGENT = "it_agent"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    """An account: ticket requester, IT agent, manager, or admin."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=True), nullable=False, default=UserRole.EMPLOYEE
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    department: Mapped["Department | None"] = relationship(back_populates="users")
    tickets_requested: Mapped[list["Ticket"]] = relationship(
        back_populates="requester", foreign_keys="Ticket.requester_id"
    )
    tickets_assigned: Mapped[list["Ticket"]] = relationship(
        back_populates="assigned_agent", foreign_keys="Ticket.assigned_agent_id"
    )
    messages: Mapped[list["TicketMessage"]] = relationship(back_populates="sender")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role.value}>"