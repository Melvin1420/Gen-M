from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import models so SQLAlchemy registers the tables.
from app import models  # noqa: F401

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.app_name,
    description=(
        "Gen-M Enterprise IT Ticketing and "
        "Asset Management API"
    ),
    version="0.1.0",
    debug=settings.app_debug,
    lifespan=lifespan,
)

@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {
        "message": "Welcome to Gen-M API",
        "documentation": "/docs",
    }

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)