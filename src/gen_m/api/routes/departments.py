from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from gen_m.api.dependencies import ActiveUser, DatabaseSession, require_role
from gen_m.models.department import Department
from gen_m.models.user import UserRole
from gen_m.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=list[DepartmentRead])
def list_departments(db: DatabaseSession, current_user: ActiveUser) -> list[Department]:
    return list(db.execute(select(Department).order_by(Department.name)).scalars())


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(department_id: int, db: DatabaseSession, current_user: ActiveUser) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return department


@router.post(
    "",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def create_department(payload: DepartmentCreate, db: DatabaseSession) -> Department:
    existing = db.execute(
        select(Department).where(Department.name == payload.name)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Department name already exists"
        )

    department = Department(name=payload.name, description=payload.description)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.patch(
    "/{department_id}",
    response_model=DepartmentRead,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
def update_department(
    department_id: int, payload: DepartmentUpdate, db: DatabaseSession
) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    data = payload.model_dump(exclude_unset=True)

    if "name" in data and data["name"] != department.name:
        clash = db.execute(
            select(Department).where(Department.name == data["name"])
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Department name already exists"
            )

    for field, value in data.items():
        setattr(department, field, value)

    db.commit()
    db.refresh(department)
    return department
