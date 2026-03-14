"""Ingest ALR boundary from BC Data Catalogue WFS."""

from __future__ import annotations

import requests
from backend.sync.config import ALR_WFS_URL, DATABASE_URL, RICHMOND_BBOX
from backend.sync.utils import get_db_connection
from shapely.geometry import shape
from shapely.validation import make_valid


async def ingest_alr() -> int:
    """Fetch ALR boundary from BC Data Catalogue WFS and insert into database.

    Returns the number of records inserted.
    """
    print("=== Ingesting ALR Boundary ===")

    bbox = RICHMOND_BBOX
    bbox_str = f"{bbox['xmin']},{bbox['ymin']},{bbox['xmax']},{bbox['ymax']}"

    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": "pub:WHSE_LEGAL_ADMIN_BOUNDARIES.OATS_ALR_POLYS",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "bbox": bbox_str,
    }

    print(f"  Fetching ALR from {ALR_WFS_URL}...")
    resp = requests.get(ALR_WFS_URL, params=params, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    features = data.get("features", [])
    print(f"  ALR features received: {len(features)}")

    conn = await get_db_connection(DATABASE_URL)
    count = 0

    try:
        await conn.execute("TRUNCATE TABLE alr_boundary RESTART IDENTITY")

        for feature in features:
            geom_json = feature.get("geometry")
            if not geom_json:
                continue

            try:
                geom = shape(geom_json)
                if not geom.is_valid:
                    geom = make_valid(geom)
                if geom.is_empty:
                    continue

                if geom.geom_type == "Polygon":
                    from shapely.geometry import MultiPolygon

                    geom = MultiPolygon([geom])

                wkt = geom.wkt
            except Exception as e:
                print(f"  ALR geometry error: {e}")
                continue

            await conn.execute(
                """
                INSERT INTO alr_boundary (geom)
                VALUES (ST_GeomFromText($1, 4326))
                """,
                wkt,
            )
            count += 1

    finally:
        await conn.close()

    print(f"  ALR boundaries ingested: {count}")
    return count
