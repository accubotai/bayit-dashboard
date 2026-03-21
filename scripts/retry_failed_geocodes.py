"""Retry geocoding for assembly candidates that failed initial geocoding.

Handles Richmond's 'No X Rd' naming convention by expanding to full road names.

Usage:
    uv run python scripts/retry_failed_geocodes.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import time

import asyncpg
import httpx

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SUPABASE_DIRECT_URL",
        "postgresql://postgres:IT5ht83AQ50xKKeKGPpOofdizQ7eBj@db.tbvypqjvaspkfgtkimlh.supabase.co:5432/postgres",
    ),
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_DELAY = 1.1


def expand_address(address: str) -> list[str]:
    """Generate search variants for Richmond addresses."""
    variants = [address]
    m = re.search(r"\bNo\s+(\d+)\s+Rd\b", address)
    if m:
        num = m.group(1)
        variants.append(re.sub(r"\bNo\s+\d+\s+Rd\b", f"Number {num} Road", address))
        variants.append(re.sub(r"\bNo\s+\d+\s+Rd\b", f"No. {num} Road", address))
        variants.append(re.sub(r"\bNo\s+\d+\s+Rd\b", f"{num} Road", address))
    return variants


async def geocode(client: httpx.AsyncClient, address: str) -> dict | None:
    """Try multiple address variants."""
    for variant in expand_address(address):
        query = f"{variant}, Richmond, BC, Canada"
        try:
            resp = await client.get(
                NOMINATIM_URL,
                params={"q": query, "format": "json", "limit": 1, "countrycodes": "ca"},
                headers={"User-Agent": "BayitDashboard/1.0"},
            )
            if resp.status_code == 200 and resp.json():
                r = resp.json()[0]
                lat, lng = float(r["lat"]), float(r["lon"])
                if 49.08 < lat < 49.23 and -123.30 < lng < -123.00:
                    return {
                        "lat": lat,
                        "lng": lng,
                        "place_type": r.get("type", ""),
                        "place_name": r.get("display_name", "").split(",")[0],
                    }
        except Exception:
            pass
        time.sleep(NOMINATIM_DELAY)
    return None


async def main() -> None:
    conn = await asyncpg.connect(DATABASE_URL)
    failed = await conn.fetch(
        "SELECT id, address FROM assembly_candidates WHERE geom IS NULL"
    )
    logger.info("Found %d failed geocodes to retry", len(failed))

    updated = 0
    async with httpx.AsyncClient(timeout=15.0) as client:
        for i, row in enumerate(failed):
            result = await geocode(client, row["address"])
            if result:
                await conn.execute(
                    """
                    UPDATE assembly_candidates
                    SET lat = $2::numeric, lng = $3::numeric,
                        geom = ST_SetSRID(ST_MakePoint($3::float, $2::float), 4326),
                        place_type = $4, place_name = $5
                    WHERE id = $1
                    """,
                    row["id"], result["lat"], result["lng"],
                    result["place_type"], result["place_name"],
                )
                logger.info("[%d/%d] FIXED %s → (%.5f, %.5f)", i + 1, len(failed), row["address"], result["lat"], result["lng"])
                updated += 1
            else:
                logger.warning("[%d/%d] STILL FAILED %s", i + 1, len(failed), row["address"])

    logger.info("Fixed %d / %d failed geocodes", updated, len(failed))

    # Run parcel matching
    result = await conn.execute(
        """
        UPDATE assembly_candidates ac
        SET matched_parcel_id = p.id, matched_pid = p.pid
        FROM parcels p
        WHERE ac.geom IS NOT NULL AND ac.matched_parcel_id IS NULL
          AND ST_Within(ac.geom, p.geom)
        """
    )
    logger.info("Parcel matching: %s", result)

    stats = await conn.fetchrow(
        "SELECT COUNT(*) as total, COUNT(geom) as geocoded, COUNT(matched_parcel_id) as matched FROM assembly_candidates"
    )
    logger.info("Final: %d total, %d geocoded, %d matched", stats["total"], stats["geocoded"], stats["matched"])
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
