"""FastAPI application for Bayit Dashboard."""

from __future__ import annotations

import typing
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.db import close_pool, get_pool
from backend.routers import auth, health, parcels, zones
from backend.routers.auth import verify_token

if typing.TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle — initialize and close DB pool."""
    await get_pool()
    yield
    await close_pool()


app = FastAPI(
    title="Bayit Dashboard API",
    description="Richmond BC Property Intelligence Dashboard",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — explicit origins, never wildcard in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Public routes (no auth required)
PUBLIC_PATHS = {"/api/health", "/api/health/db", "/api/login", "/api/auth/check", "/api/logout"}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Require authentication for protected API endpoints."""
    path = request.url.path
    # Allow public paths and non-API paths (frontend static files)
    if not path.startswith("/api/") or path in PUBLIC_PATHS:
        return await call_next(request)

    token = request.cookies.get("session", "")
    if not verify_token(token):
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

    return await call_next(request)


app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(parcels.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
