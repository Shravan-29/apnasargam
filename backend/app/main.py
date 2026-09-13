from fastapi import FastAPI

from app.core.config import settings
from app.api.v1 import projects

app = FastAPI(title=settings.app_name)

app.include_router(projects.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}