"""Refresh the enriched_parcels materialized view."""

from __future__ import annotations

import asyncio
import time

from backend.sync.config import DATABASE_URL
from backend.sync.utils import get_db_connection


async def main() -> None:
    """Refresh the enriched_parcels materialized view concurrently."""
    print("Refreshing enriched_parcels materialized view...")
    start = time.time()

    conn = await get_db_connection(DATABASE_URL)

    try:
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY enriched_parcels")
        count = await conn.fetchval("SELECT COUNT(*) FROM enriched_parcels")
        elapsed = time.time() - start
        print(f"Done in {elapsed:.1f}s — enriched_parcels now has {count} rows.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
