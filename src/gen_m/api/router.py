from fastapi import APIRouter

from gen_m.api.routes import auth, health, tickets

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tickets.router)
