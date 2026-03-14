"""Shared utilities for data ingestion: ArcGIS pagination, geometry validation."""

from __future__ import annotations

import time

import asyncpg
import requests
from backend.sync.config import ARCGIS_PAGE_SIZE
from shapely.geometry import shape
from shapely.validation import make_valid


def fetch_arcgis_all(
    url: str,
    where: str = "1=1",
    out_fields: str = "*",
    page_size: int = ARCGIS_PAGE_SIZE,
) -> list[dict]:
    """Fetch all records from an ArcGIS REST FeatureServer with pagination.

    Always requests outSR=4326 (WGS84) and GeoJSON format.
    """
    all_features: list[dict] = []
    offset = 0

    while True:
        params = {
            "where": where,
            "outFields": out_fields,
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        }

        print(f"  Fetching offset={offset}...")
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        features = data.get("features", [])
        if not features:
            break

        all_features.extend(features)
        offset += len(features)

        # ArcGIS signals no more records when fewer than page_size returned
        if len(features) < page_size:
            break

        # Rate limiting courtesy
        time.sleep(0.5)

    print(f"  Total features fetched: {len(all_features)}")
    return all_features


def validate_and_fix_geometry(geojson_geom: dict) -> str | None:
    """Validate a GeoJSON geometry, fix if invalid, return as WKT.

    Returns None if geometry is completely invalid.
    """
    try:
        geom = shape(geojson_geom)
        if not geom.is_valid:
            geom = make_valid(geom)
        if geom.is_empty:
            return None
        # Force to MultiPolygon for consistency
        if geom.geom_type == "Polygon":
            from shapely.geometry import MultiPolygon

            geom = MultiPolygon([geom])
        return geom.wkt
    except Exception as e:
        print(f"  Geometry validation failed: {e}")
        return None


def simplify_geometry(geojson_geom: dict, tolerance: float = 0.00001) -> str | None:
    """Simplify geometry to reduce storage size, return as WKT."""
    try:
        geom = shape(geojson_geom)
        if not geom.is_valid:
            geom = make_valid(geom)
        if geom.is_empty:
            return None
        geom = geom.simplify(tolerance, preserve_topology=True)
        if geom.geom_type == "Polygon":
            from shapely.geometry import MultiPolygon

            geom = MultiPolygon([geom])
        return geom.wkt
    except Exception as e:
        print(f"  Geometry simplification failed: {e}")
        return None


async def get_db_connection(dsn: str) -> asyncpg.Connection:
    """Create a direct database connection for bulk operations."""
    return await asyncpg.connect(dsn)
