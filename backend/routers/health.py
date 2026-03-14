"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from backend.config import settings
from backend.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(status="ok", environment=settings.environment)
