"""Main API router combining all endpoint routers."""

from fastapi import APIRouter

from app.api.resume import router as resume_router
from app.api.health import router as health_router

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])
