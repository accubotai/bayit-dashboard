"""Ingest parcels from Richmond GeoHub ArcGIS REST API."""

from __future__ import annotations

from backend.sync.config import DATABASE_URL, GEOHUB_PARCELS_URL
from backend.sync.utils import fetch_arcgis_all, get_db_connection, simplify_geometry


async def ingest_parcels() -> int:
    """Fetch all parcels from GeoHub and upsert into database.

    Returns the number of records inserted/updated.
    """
    print("=== Ingesting Parcels ===")

    features = fetch_arcgis_all(
        GEOHUB_PARCELS_URL,
        out_fields="PID,CIVIC_ADDRESS,OWNER,LOT_AREA",
    )

    conn = await get_db_connection(DATABASE_URL)
    count = 0

    try:
        for feature in features:
            props = feature.get("properties", {})
            geom = feature.get("geometry")

            if not geom:
                continue

            wkt = simplify_geometry(geom)
            if not wkt:
                continue

            pid_raw = props.get("PID", "")
            pid = str(pid_raw).strip() if pid_raw else None

            # Format PID as XXX-XXX-XXX if it's 9 digits
            if pid and pid.isdigit() and len(pid) == 9:
                pid = f"{pid[:3]}-{pid[3:6]}-{pid[6:9]}"

            owner = props.get("OWNER", "")
            owner_type = "Municipal" if owner and "CITY OF RICHMOND" in str(owner).upper() else "Private"

            lot_area = props.get("LOT_AREA")
            if lot_area is not None:
                try:
                    lot_area = float(lot_area)
                except (ValueError, TypeError):
                    lot_area = None

            await conn.execute(
                """
                INSERT INTO parcels (pid, civic_address, owner_name, lot_area_sqm, geom, source, owner_type)
                VALUES ($1, $2, $3, $4, ST_GeomFromText($5, 4326), 'geohub', $6)
                ON CONFLICT (pid) DO UPDATE SET
                    civic_address = EXCLUDED.civic_address,
                    owner_name = EXCLUDED.owner_name,
                    lot_area_sqm = EXCLUDED.lot_area_sqm,
                    geom = EXCLUDED.geom,
                    owner_type = EXCLUDED.owner_type,
                    last_synced = NOW()
                """,
                pid,
                props.get("CIVIC_ADDRESS"),
                owner,
                lot_area,
                wkt,
                owner_type,
            )
            count += 1

    finally:
        await conn.close()

    print(f"  Parcels ingested: {count}")
    return count
