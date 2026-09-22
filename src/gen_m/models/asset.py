from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING 

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gen_m.database.base import Base

if TYPE_CHECKING:
    from gen_m.models.department import Department
    from gen_m.models.ticket import Ticket
    from gen_m.models.user import User

class AssetStatus(str, enum.Enum):
    IN_USE = "in_use"
    IN_STORAGE = "in_storage"
    UNDER_REPAIR = "under_repair"
    RETIRED = "retired"

class Asset(Base):
    """A tracked piece of equipment (laptop, monitor, phone, etc.)."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_tag: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(150))
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus, native_enum=True), nullable=False, default=AssetStatus.IN_STORAGE
    )

    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))

    purchase_date: Mapped[date | None] = mapped_column(Date)
    warranty_expiry: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    assigned_to: Mapped["User | None"] = relationship()
    department: Mapped["Department | None"] = relationship()
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="asset")

    def __repr__(self) -> str:
        return f"<Asset id={self.id} tag={self.asset_tag!r} status={self.status.value}>"
