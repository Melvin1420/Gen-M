from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gen_m.database.base import Base

if TYPE_CHECKING:
    from gen_m.models.ticket import Ticket
    from gen_m.models.user import User


class Department(Base):
    """A Department that owns a ticket queue (e.g. Networking, Hardware, Access)."""

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now() 
    )

    users: Mapped[list["User"]] = relationship(back_populates="department")
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"
    
