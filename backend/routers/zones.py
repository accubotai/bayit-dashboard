"""Zoning districts API endpoint."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query

from backend.config import validate_bbox
from backend.db import get_pool
from backend.models import ZoneCollection, ZoneFeature, ZoneProperties

router = APIRouter(tags=["zones"])


@router.get("/zones", response_model=ZoneCollection)
async def get_zones(
    bbox: str = Query(
        ...,
        description="Bounding box: min_lng,min_lat,max_lng,max_lat",
        pattern=r"^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$",
    ),
    permits_assembly: bool | None = Query(None, description="Filter by assembly permission"),
) -> ZoneCollection:
    """Return zoning districts within a bounding box as GeoJSON FeatureCollection."""
    parts = bbox.split(",")
    min_lng, min_lat, max_lng, max_lat = (float(p) for p in parts)

    try:
        validate_bbox(min_lng, min_lat, max_lng, max_lat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    conditions = ["ST_Intersects(geom, ST_MakeEnvelope($1, $2, $3, $4, 4326))"]
    params: list[float | bool] = [min_lng, min_lat, max_lng, max_lat]
    param_idx = 5

    if permits_assembly is not None:
        conditions.append(f"permits_assembly = ${param_idx}")
        params.append(permits_assembly)

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
            id, zone_code, zone_description, permits_assembly,
            max_far, max_height_m,
            ST_AsGeoJSON(ST_Simplify(geom, 0.00001))::json AS geojson
        FROM zoning_districts
        WHERE {where_clause}
    """  # noqa: S608

    pool = await get_pool()
    rows = await pool.fetch(query, *params)

    features = []
    for row in rows:
        geojson = row["geojson"] if isinstance(row["geojson"], dict) else json.loads(row["geojson"])
        features.append(
            ZoneFeature(
                geometry=geojson,
                properties=ZoneProperties(
                    id=row["id"],
                    zone_code=row["zone_code"],
                    zone_description=row["zone_description"],
                    permits_assembly=row["permits_assembly"],
                    max_far=float(row["max_far"]) if row["max_far"] else None,
                    max_height_m=float(row["max_height_m"]) if row["max_height_m"] else None,
                ),
            )
        )

    return ZoneCollection(type="FeatureCollection", features=features)
