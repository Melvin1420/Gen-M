from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_database_session

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)

@router.get("")
def health_check(
    database: Session = Depends(get_database_session),
) -> dict[str, str]:
    database.execute(text("SELECT 1"))
    return {
        "status": "healthy",
        "application": "Gen-M",
        "database": "connected",
    }
    