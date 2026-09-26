from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from gen_m.models.asset import AssetStatus


class AssetCreate(BaseModel):
    asset_tag: str
    name: str
    category: str
    serial_number: str | None = None
    status: AssetStatus = AssetStatus.IN_STORAGE
    assigned_to_id: int | None = None
    department_id: int | None = None
    purchase_date: date | None = None
    warranty_expiry: date | None = None


class AssetUpdate(BaseModel):
    asset_tag: str | None = None
    name: str | None = None
    category: str | None = None
    serial_number: str | None = None
    status: AssetStatus | None = None
    assigned_to_id: int | None = None
    department_id: int | None = None
    purchase_date: date | None = None
    warranty_expiry: date | None = None


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    asset_tag: str
    name: str
    category: str
    serial_number: str | None
    status: AssetStatus
    assigned_to_id: int | None
    department_id: int | None
    purchase_date: date | None
    warranty_expiry: date | None
    created_at: datetime
    updated_at: datetime
