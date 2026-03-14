"""Database connection using asyncpg."""

from __future__ import annotations

import logging

import asyncpg

from backend.config import settings

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Get or create the connection pool.

    Uses statement_cache_size=0 for Supabase pgbouncer compatibility.
    On serverless (Vercel), each cold start creates a new pool with min_size=0.
    """
    global _pool
    if _pool is None:
        logger.info("Creating connection pool to %s", settings.db_url[:40] + "...")
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
        await _pool.close()
        _pool = None
