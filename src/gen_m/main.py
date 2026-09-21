from fastapi import FastAPI

from gen_m.api.router import api_router
from gen_m.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

app.include_router(api_router)

@app.get("/")
def root():
    return {"app": settings.app_name, "env": settings.app_env}