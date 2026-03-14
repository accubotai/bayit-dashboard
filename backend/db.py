"""Database connection using asyncpg."""

from __future__ import annotations

import asyncio
import contextlib
import logging

import asyncpg

from backend.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the connection pool.

    Uses statement_cache_size=0 for Supabase pgbouncer compatibility.
    Recreates pool if the event loop has changed (serverless cold start).
    """
    global _pool
    try:
        if _pool is not None:
            # Test if pool is still usable
            async with _pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return _pool
    except Exception:
        # Pool is stale (event loop closed, connection dropped, etc.)
        logger.info("Stale pool detected, recreating...")
        _pool = None

    loop = asyncio.get_running_loop()
    logger.info("Creating connection pool on loop %s", id(loop))
    _pool = await asyncpg.create_pool(
        dsn=settings.db_url,
        min_size=0,
        max_size=3,
        statement_cache_size=0,
        command_timeout=8,
    )
    return _pool


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        with contextlib.suppress(Exception):
            await _pool.close()
        _pool = None
