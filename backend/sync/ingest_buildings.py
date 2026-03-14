"""Ingest building footprints from Richmond GeoHub ArcGIS REST API."""

from __future__ import annotations

from backend.sync.config import DATABASE_URL, GEOHUB_BUILDINGS_URL
from backend.sync.utils import fetch_arcgis_all, get_db_connection, simplify_geometry


async def ingest_buildings() -> int:
    """Fetch all building footprints from GeoHub and insert into database.

    Returns the number of records inserted.
    """
    print("=== Ingesting Building Footprints ===")

    features = fetch_arcgis_all(GEOHUB_BUILDINGS_URL)

    conn = await get_db_connection(DATABASE_URL)
    count = 0

    try:
        # Clear existing and re-insert
        await conn.execute("TRUNCATE TABLE building_footprints RESTART IDENTITY")

        for feature in features:
            geom = feature.get("geometry")
            if not geom:
                continue

            wkt = simplify_geometry(geom)
            if not wkt:
                continue

            await conn.execute(
                """
                INSERT INTO building_footprints (geom)
                VALUES (ST_GeomFromText($1, 4326))
                """,
                wkt,
            )
            count += 1

    finally:
        await conn.close()

    print(f"  Building footprints ingested: {count}")
    return count
