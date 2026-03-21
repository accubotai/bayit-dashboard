"""Ingest 'Properties zoned to permit Religious Assembly' CSV into Supabase.

Geocodes addresses via Nominatim, spatially matches to existing parcels,
and enriches with OSM place info (what's currently at each location).

Usage:
    uv run python scripts/ingest_assembly_csv.py
"""

from __future__ import annotations

import asyncio
import csv
import json
import logging
import os
import sys
import time

import asyncpg
import httpx

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SUPABASE_DIRECT_URL",
        "postgresql://user:password@localhost:5432/richmond_land",
    ),
)

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "Properties zoned to permit Religious Assembly.csv",
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# Be polite: 1 request per second per Nominatim usage policy
NOMINATIM_DELAY = 1.1


def _expand_richmond_roads(address: str) -> list[str]:
    """Generate address variants for Richmond's 'No X Rd' naming convention."""
    import re
    variants = [address]
    # "No 3 Rd" → "Number 3 Road", "No. 3 Road"
    m = re.search(r'\bNo\s+(\d+)\s+Rd\b', address)
    if m:
        num = m.group(1)
        variants.append(re.sub(r'\bNo\s+\d+\s+Rd\b', f'Number {num} Road', address))
        variants.append(re.sub(r'\bNo\s+\d+\s+Rd\b', f'No. {num} Road', address))
    return variants


async def geocode_address(client: httpx.AsyncClient, address: str) -> dict | None:
    """Geocode a Richmond BC address via Nominatim."""
    variants = _expand_richmond_roads(address)
    for variant in variants:
        query = f"{variant}, Richmond, BC, Canada"
        try:
            resp = await client.get(
                NOMINATIM_URL,
                params={
                    "q": query,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "ca",
                    "addressdetails": 1,
                },
                headers={"User-Agent": "BayitDashboard/1.0 (synagogue site search)"},
            )
            if resp.status_code == 200 and resp.json():
                result = resp.json()[0]
                return {
                    "lat": float(result["lat"]),
                    "lng": float(result["lon"]),
                    "place_type": result.get("type", ""),
                    "place_name": result.get("display_name", "").split(",")[0],
                }
        except Exception as e:
            logger.warning("Geocode failed for %s: %s", variant, e)
        if len(variants) > 1:
            time.sleep(NOMINATIM_DELAY)
    return None


async def reverse_lookup_osm(
    client: httpx.AsyncClient, lat: float, lng: float
) -> dict:
    """Get OSM details about what's at a specific location."""
    try:
        resp = await client.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lng,
                "format": "json",
                "zoom": 18,
                "addressdetails": 1,
            },
            headers={"User-Agent": "BayitDashboard/1.0 (synagogue site search)"},
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "place_type": data.get("type", ""),
                "place_name": data.get("display_name", "").split(",")[0],
            }
    except Exception:
        pass
    return {"place_type": "", "place_name": ""}


async def create_table(conn: asyncpg.Connection) -> None:
    """Create the assembly_candidates table if it doesn't exist."""
    migration_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sql/migrations/005_create_assembly_candidates.sql",
    )
    with open(migration_path) as f:
        sql = f.read()
    await conn.execute(sql)
    logger.info("Table assembly_candidates ready")


async def main() -> None:
    """Main ingestion flow."""
    # Read CSV
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    logger.info("Read %d rows from CSV (%d unique addresses)", len(rows), len(set(r["Address"] for r in rows)))

    # Deduplicate by address (some addresses appear with multiple zone codes)
    # Group zones per address
    addr_zones: dict[str, set[str]] = {}
    for row in rows:
        addr = row["Address"].strip()
        zoning = row["Zoning"].strip()
        addr_zones.setdefault(addr, set()).add(zoning)

    unique_entries: list[dict[str, str]] = []
    for addr, zones in addr_zones.items():
        unique_entries.append({"address": addr, "zoning": ", ".join(sorted(zones))})

    logger.info("Deduplicated to %d unique addresses", len(unique_entries))

    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await create_table(conn)

        # Check what's already ingested
        existing = await conn.fetch(
            "SELECT address FROM assembly_candidates"
        )
        existing_addrs = {r["address"] for r in existing}
        to_process = [e for e in unique_entries if e["address"] not in existing_addrs]
        logger.info(
            "%d already in DB, %d to process", len(existing_addrs), len(to_process)
        )

        if not to_process:
            logger.info("All addresses already ingested. Done.")
            # Still do parcel matching for any unmatched
            await match_parcels(conn)
            return

        async with httpx.AsyncClient(timeout=15.0) as client:
            for i, entry in enumerate(to_process):
                addr = entry["address"]
                zoning = entry["zoning"]

                # Geocode
                geo = await geocode_address(client, addr)
                if geo is None:
                    logger.warning("[%d/%d] SKIP %s — geocode failed", i + 1, len(to_process), addr)
                    # Insert without coords — can retry later
                    await conn.execute(
                        """
                        INSERT INTO assembly_candidates (address, zoning)
                        VALUES ($1, $2)
                        ON CONFLICT DO NOTHING
                        """,
                        addr, zoning,
                    )
                    time.sleep(NOMINATIM_DELAY)
                    continue

                lat, lng = geo["lat"], geo["lng"]

                # Verify it's actually in Richmond (roughly)
                if not (49.08 < lat < 49.23 and -123.30 < lng < -123.00):
                    logger.warning(
                        "[%d/%d] SKIP %s — geocoded outside Richmond (%.4f, %.4f)",
                        i + 1, len(to_process), addr, lat, lng,
                    )
                    await conn.execute(
                        """
                        INSERT INTO assembly_candidates (address, zoning, notes)
                        VALUES ($1, $2, $3)
                        ON CONFLICT DO NOTHING
                        """,
                        addr, zoning, f"Geocoded outside Richmond: {lat},{lng}",
                    )
                    time.sleep(NOMINATIM_DELAY)
                    continue

                # Insert with geometry
                await conn.execute(
                    """
                    INSERT INTO assembly_candidates (address, zoning, lat, lng, geom, place_type, place_name)
                    VALUES ($1, $2, $3::numeric, $4::numeric,
                            ST_SetSRID(ST_MakePoint($4::float, $3::float), 4326),
                            $5, $6)
                    ON CONFLICT DO NOTHING
                    """,
                    addr,
                    zoning,
                    lat,
                    lng,
                    geo["place_type"],
                    geo["place_name"],
                )

                logger.info(
                    "[%d/%d] %s → (%.5f, %.5f) %s",
                    i + 1, len(to_process), addr, lat, lng,
                    geo.get("place_name", ""),
                )

                # Nominatim rate limit
                time.sleep(NOMINATIM_DELAY)

        # Spatial match to parcels
        await match_parcels(conn)

    finally:
        await conn.close()


async def match_parcels(conn: asyncpg.Connection) -> None:
    """Spatially match assembly candidates to parcels (point-in-polygon)."""
    updated = await conn.execute(
        """
        UPDATE assembly_candidates ac
        SET matched_parcel_id = p.id,
            matched_pid = p.pid
        FROM parcels p
        WHERE ac.geom IS NOT NULL
          AND ac.matched_parcel_id IS NULL
          AND ST_Within(ac.geom, p.geom)
        """
    )
    logger.info("Parcel matching: %s", updated)

    # Stats
    stats = await conn.fetchrow(
        """
        SELECT
            COUNT(*) as total,
            COUNT(geom) as geocoded,
            COUNT(matched_parcel_id) as matched
        FROM assembly_candidates
        """
    )
    logger.info(
        "Assembly candidates: %d total, %d geocoded, %d matched to parcels",
        stats["total"], stats["geocoded"], stats["matched"],
    )


if __name__ == "__main__":
    asyncio.run(main())
