"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health status."""
    settings = get_settings()
    return HealthResponse(status="healthy", version=settings.APP_VERSION)
