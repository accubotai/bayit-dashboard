"""Health check endpoint."""

from __future__ import annotations

import httpx
from fastapi import APIRouter

from backend.config import settings
from backend.db import SUPABASE_KEY, SUPABASE_URL, get_pool, use_rest
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
        if use_rest():
            async with httpx.AsyncClient(timeout=9.0) as client:
                resp = await client.get(
                    f"{SUPABASE_URL}/rest/v1/parcels?select=count&limit=1",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Prefer": "count=exact",
                    },
                )
                count = resp.headers.get("content-range", "*/0").split("/")[-1]
                return {"status": "ok", "parcels_count": int(count), "mode": "rest"}
        pool = await get_pool()
        row = await pool.fetchval("SELECT COUNT(*) FROM parcels")
        return {"status": "ok", "parcels_count": row, "mode": "asyncpg"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
