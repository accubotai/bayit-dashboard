"""Ingest parcels from ParcelMap BC via BC Data Catalogue WFS."""

from __future__ import annotations

import requests

from backend.sync.config import (
    BC_PARCELS_LAYER,
    BC_PARCELS_WFS_URL,
    DATABASE_URL,
    RICHMOND_BBOX,
)
from backend.sync.utils import get_db_connection, simplify_geometry


async def ingest_parcels() -> int:
    """Fetch all Richmond parcels from ParcelMap BC WFS and upsert into database.

    The BC WFS does not support startIndex pagination, so we fetch all parcels
    in a single request. Richmond has ~60k parcels which is within WFS limits.

    Returns the number of records inserted/updated.
    """
    print("=== Ingesting Parcels (ParcelMap BC WFS) ===")

    bbox = RICHMOND_BBOX
    bbox_str = f"{bbox['xmin']},{bbox['ymin']},{bbox['xmax']},{bbox['ymax']},EPSG:4326"

    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": BC_PARCELS_LAYER,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": bbox_str,
    }

    print("  Fetching all Richmond parcels (this may take a few minutes)...")
    resp = requests.get(BC_PARCELS_WFS_URL, params=params, timeout=600)
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features", [])
    print(f"  Features received: {len(features)}")

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

            pid = props.get("PID_FORMATTED") or props.get("PID")
            if not pid:
                continue

            owner_type = props.get("OWNER_TYPE", "Private")
            lot_area = props.get("FEATURE_AREA_SQM")

            await conn.execute(
                """
                INSERT INTO parcels (pid, civic_address, owner_name, lot_area_sqm,
                                     geom, source, owner_type)
                VALUES ($1, $2, $3, $4, ST_GeomFromText($5, 4326), 'parcelmap_bc', $6)
                ON CONFLICT (pid) DO UPDATE SET
                    lot_area_sqm = EXCLUDED.lot_area_sqm,
                    geom = EXCLUDED.geom,
                    owner_type = EXCLUDED.owner_type,
                    last_synced = NOW()
                """,
                str(pid),
                None,
                None,
                float(lot_area) if lot_area else None,
                wkt,
                owner_type,
            )
            count += 1

    finally:
        await conn.close()

    print(f"  Parcels ingested: {count}")
    return count
