from fastapi import APIRouter

from gen_m.api.routes import assets, auth, departments, health, tickets, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(tickets.router)
api_router.include_router(departments.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
