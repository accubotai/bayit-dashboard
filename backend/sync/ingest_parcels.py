"""Ingest Richmond parcels from ParcelMap BC via BC Data Catalogue WFS.

Strategy:
- Filter by MUNICIPALITY='Richmond, City of' (not just bbox)
- Split into grid tiles to stay under the 10k WFS response cap
- Upsert by PID — safe to re-run for incremental updates
- Supports --since flag to only fetch parcels updated after a date
"""

from __future__ import annotations

import time

import requests

from backend.sync.config import (
    BC_PARCELS_LAYER,
    BC_PARCELS_WFS_URL,
    DATABASE_URL,
    RICHMOND_BBOX,
    RICHMOND_MUNICIPALITY,
    WFS_GRID_COLS,
    WFS_GRID_ROWS,
)
from backend.sync.utils import get_db_connection, simplify_geometry


def _build_cql_filter(since: str | None = None) -> str:
    """Build CQL_FILTER for Richmond parcels, optionally since a date."""
    cql = f"MUNICIPALITY='{RICHMOND_MUNICIPALITY}'"
    if since:
        cql += f" AND WHEN_UPDATED >= '{since}'"
    return cql


def _fetch_tile(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    cql_filter: str,
) -> list[dict]:
    """Fetch parcels for one bbox tile from WFS."""
    # Combine municipality filter with BBOX in CQL_FILTER
    # (WFS doesn't support bbox param + CQL_FILTER together)
    tile_cql = f"{cql_filter} AND BBOX(SHAPE,{xmin},{ymin},{xmax},{ymax},'EPSG:4326')"
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeName": BC_PARCELS_LAYER,
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "CQL_FILTER": tile_cql,
    }

    resp = requests.get(BC_PARCELS_WFS_URL, params=params, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    return data.get("features", [])


async def _upsert_features(conn, features: list[dict]) -> int:
    """Upsert parcel features into the database. Returns count inserted."""
    count = 0
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
    return count


async def ingest_parcels(since: str | None = None) -> int:
    """Fetch Richmond parcels from ParcelMap BC WFS using grid tiles.

    Args:
        since: Optional ISO date (e.g. '2025-01-01') to only fetch
               parcels updated after this date (incremental sync).

    Returns the number of records inserted/updated.
    """
    mode = f"incremental since {since}" if since else "full sync"
    print(f"=== Ingesting Richmond Parcels ({mode}) ===")

    cql_filter = _build_cql_filter(since)
    print(f"  CQL_FILTER: {cql_filter}")

    bbox = RICHMOND_BBOX
    dx = (bbox["xmax"] - bbox["xmin"]) / WFS_GRID_COLS
    dy = (bbox["ymax"] - bbox["ymin"]) / WFS_GRID_ROWS

    conn = await get_db_connection(DATABASE_URL)
    total_fetched = 0
    total_inserted = 0
    tiles = WFS_GRID_COLS * WFS_GRID_ROWS

    try:
        # Clear stale data only on full sync
        if not since:
            stale = await conn.fetchval("SELECT COUNT(*) FROM parcels WHERE source = 'parcelmap_bc'")
            print(f"  Existing parcels in DB: {stale}")

        for row in range(WFS_GRID_ROWS):
            for col in range(WFS_GRID_COLS):
                tile_num = row * WFS_GRID_COLS + col + 1
                xmin = bbox["xmin"] + col * dx
                ymin = bbox["ymin"] + row * dy
                xmax = xmin + dx
                ymax = ymin + dy

                print(
                    f"  Tile {tile_num}/{tiles} [{xmin:.3f},{ymin:.3f} → {xmax:.3f},{ymax:.3f}]...",
                    end=" ",
                    flush=True,
                )

                features = _fetch_tile(xmin, ymin, xmax, ymax, cql_filter)
                inserted = await _upsert_features(conn, features)
                total_fetched += len(features)
                total_inserted += inserted

                warning = " ⚠ HIT 10K CAP" if len(features) >= 10000 else ""
                print(f"fetched={len(features)}, inserted={inserted}{warning}")

                time.sleep(0.3)

    finally:
        await conn.close()

    print(f"\n  Total fetched: {total_fetched}")
    print(f"  Total upserted: {total_inserted}")
    return total_inserted
