from fastapi import APIRouter
from sqlalchemy import text

from gen_m.api.dependencies import DatabaseSession

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(db: DatabaseSession):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}