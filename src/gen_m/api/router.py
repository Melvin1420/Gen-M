from fastapi import APIRouter

from gen_m.api.routes import health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
