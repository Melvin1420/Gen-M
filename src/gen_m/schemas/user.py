from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from gen_m.models.user import UserRole


class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.EMPLOYEE
    department_id: int | None = None


class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    department_id: int | None = None
    is_active: bool | None = None
    password: str | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    department_id: int | None
    created_at: datetime
    updated_at: datetime
