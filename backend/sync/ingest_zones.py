"""Ingest zoning districts from Richmond GeoHub ArcGIS REST API."""

from __future__ import annotations

from backend.sync.config import DATABASE_URL, GEOHUB_ZONING_URL
from backend.sync.utils import fetch_arcgis_all, get_db_connection, simplify_geometry


async def ingest_zones() -> int:
    """Fetch all zoning districts from GeoHub and insert into database.

    Returns the number of records inserted.
    """
    print("=== Ingesting Zoning Districts ===")

    features = fetch_arcgis_all(
        GEOHUB_ZONING_URL,
        out_fields="ZONE_CODE,ZONE_DESCRIPTION",
    )

    conn = await get_db_connection(DATABASE_URL)
    count = 0

    try:
        # Clear existing and re-insert (zoning rarely changes)
        await conn.execute("TRUNCATE TABLE zoning_districts RESTART IDENTITY")

        for feature in features:
            props = feature.get("properties", {})
            geom = feature.get("geometry")

            if not geom:
                continue

            wkt = simplify_geometry(geom)
            if not wkt:
                continue

            zone_code = props.get("ZONE_CODE", "")

            # Check if this zone permits assembly use
            result = await conn.fetchval(
                """
                SELECT permission_type FROM zone_use_permissions
                WHERE zone_code = $1 AND use_category = 'assembly'
                """,
                zone_code,
            )
            permits_assembly = result in ("permitted", "conditional")

            await conn.execute(
                """
                INSERT INTO zoning_districts (zone_code, zone_description, permits_assembly, geom)
                VALUES ($1, $2, $3, ST_GeomFromText($4, 4326))
                """,
                zone_code,
                props.get("ZONE_DESCRIPTION", ""),
                permits_assembly,
                wkt,
            )
            count += 1

    finally:
        await conn.close()

    print(f"  Zoning districts ingested: {count}")
    return count
