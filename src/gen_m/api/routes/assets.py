from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from gen_m.api.dependencies import ActiveUser, DatabaseSession, require_role
from gen_m.models.asset import Asset
from gen_m.models.department import Department
from gen_m.models.user import User, UserRole
from gen_m.schemas.asset import AssetCreate, AssetRead, AssetUpdate

router = APIRouter(prefix="/assets", tags=["assets"])

STAFF_ROLES = (UserRole.IT_AGENT, UserRole.ADMIN)


def _can_view(user: User, asset: Asset) -> bool:
    if user.role in (UserRole.ADMIN, UserRole.IT_AGENT):
        return True
    if user.role == UserRole.MANAGER:
        return asset.department_id == user.department_id
    return asset.assigned_to_id == user.id


def _validate_refs(
    db: DatabaseSession, assigned_to_id: int | None, department_id: int | None
) -> None:
    if assigned_to_id is not None and db.get(User, assigned_to_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if department_id is not None and db.get(Department, department_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")


@router.post(
    "",
    response_model=AssetRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def create_asset(payload: AssetCreate, db: DatabaseSession) -> Asset:
    existing = db.execute(
        select(Asset).where(Asset.asset_tag == payload.asset_tag)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Asset tag already exists"
        )

    _validate_refs(db, payload.assigned_to_id, payload.department_id)

    asset = Asset(
        asset_tag=payload.asset_tag,
        name=payload.name,
        category=payload.category,
        serial_number=payload.serial_number,
        status=payload.status,
        assigned_to_id=payload.assigned_to_id,
        department_id=payload.department_id,
        purchase_date=payload.purchase_date,
        warranty_expiry=payload.warranty_expiry,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("", response_model=list[AssetRead])
def list_assets(db: DatabaseSession, current_user: ActiveUser) -> list[Asset]:
    stmt = select(Asset)

    if current_user.role in (UserRole.ADMIN, UserRole.IT_AGENT):
        pass
    elif current_user.role == UserRole.MANAGER:
        stmt = stmt.where(Asset.department_id == current_user.department_id)
    else:
        stmt = stmt.where(Asset.assigned_to_id == current_user.id)

    return list(db.execute(stmt.order_by(Asset.asset_tag)).scalars())


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(asset_id: int, db: DatabaseSession, current_user: ActiveUser) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")
    if not _can_view(current_user, asset):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return asset


@router.patch(
    "/{asset_id}",
    response_model=AssetRead,
    dependencies=[Depends(require_role(*STAFF_ROLES))],
)
def update_asset(asset_id: int, payload: AssetUpdate, db: DatabaseSession) -> Asset:
    asset = db.get(Asset, asset_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

    data = payload.model_dump(exclude_unset=True)

    if "asset_tag" in data and data["asset_tag"] != asset.asset_tag:
        clash = db.execute(
            select(Asset).where(Asset.asset_tag == data["asset_tag"])
        ).scalar_one_or_none()
        if clash is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Asset tag already exists"
            )

    _validate_refs(db, data.get("assigned_to_id"), data.get("department_id"))

    for field, value in data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset
