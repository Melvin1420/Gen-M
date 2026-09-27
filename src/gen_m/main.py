from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from gen_m.api.router import api_router
from gen_m.core.config import settings

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.get("/api")
def api_info() -> dict[str, str]:
    return {"app": settings.app_name, "env": settings.app_env}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
