"""Database access — asyncpg pool for local dev, Supabase REST for serverless."""

from __future__ import annotations

import contextlib
import logging
import os

import asyncpg

from backend.config import settings

logger = logging.getLogger(__name__)

# Supabase REST API credentials (set on Vercel, absent locally)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

_pool: asyncpg.Pool | None = None


def use_rest() -> bool:
    """Whether to use Supabase REST API instead of asyncpg."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


async def get_pool() -> asyncpg.Pool:
    """Get or create the asyncpg connection pool (local/direct connections)."""
    global _pool
    try:
        if _pool is not None:
            async with _pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return _pool
    except Exception:
        logger.info("Stale pool, recreating...")
        _pool = None

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
