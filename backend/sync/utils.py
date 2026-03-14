"""Shared utilities for data ingestion: geometry validation, DB connection."""

from __future__ import annotations

import asyncpg
from shapely.geometry import MultiPolygon, shape
from shapely.validation import make_valid


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
            geom = MultiPolygon([geom])
        return geom.wkt
    except Exception as e:
        print(f"  Geometry simplification failed: {e}")
        return None


async def get_db_connection(dsn: str) -> asyncpg.Connection:
    """Create a direct database connection for bulk operations."""
    return await asyncpg.connect(dsn)
