"""FastAPI application for Bayit Dashboard."""

from __future__ import annotations

import typing
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db import close_pool, get_pool
from backend.routers import health, parcels, zones

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
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(parcels.router, prefix="/api")
app.include_router(zones.router, prefix="/api")
