"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from backend.config import settings
from backend.db import get_pool
from backend.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return application health status."""
    return HealthResponse(status="ok", environment=settings.environment)


@router.get("/health/db")
async def health_db() -> dict:
    """Check database connectivity."""
    try:
        pool = await get_pool()
        row = await pool.fetchval("SELECT COUNT(*) FROM parcels")
        return {"status": "ok", "parcels_count": row, "db_url_prefix": settings.db_url[:50]}
    except Exception as e:
        return {"status": "error", "error": str(e), "db_url_prefix": settings.db_url[:50]}
