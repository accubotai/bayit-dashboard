"""Parcels API endpoint — returns enriched parcels as GeoJSON."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query

from backend.config import validate_bbox
from backend.db import get_pool
from backend.models import GeoJSONFeature, ParcelCollection, ParcelProperties

router = APIRouter(tags=["parcels"])


@router.get("/parcels", response_model=ParcelCollection)
async def get_parcels(
    bbox: str = Query(
        ...,
        description="Bounding box: min_lng,min_lat,max_lng,max_lat",
        pattern=r"^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$",
    ),
    limit: int = Query(500, ge=1, le=2000),
    owner_type: str | None = Query(None, description="Filter by owner type"),
    permits_assembly: bool | None = Query(None, description="Filter by assembly permission"),
    no_building: bool | None = Query(None, description="Filter for vacant parcels"),
    exclude_alr: bool = Query(False, description="Exclude ALR parcels"),
) -> ParcelCollection:
    """Return enriched parcels within a bounding box as GeoJSON FeatureCollection."""
    parts = bbox.split(",")
    min_lng, min_lat, max_lng, max_lat = (float(p) for p in parts)

    try:
        validate_bbox(min_lng, min_lat, max_lng, max_lat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Build query with parameterized filters
    conditions = ["ST_Intersects(geom, ST_MakeEnvelope($1, $2, $3, $4, 4326))"]
    params: list[float | str | bool] = [min_lng, min_lat, max_lng, max_lat]
    param_idx = 5

    if owner_type is not None:
        conditions.append(f"owner_type = ${param_idx}")
        params.append(owner_type)
        param_idx += 1

    if permits_assembly is not None:
        conditions.append(f"permits_assembly = ${param_idx}")
        params.append(permits_assembly)
        param_idx += 1

    if no_building is not None:
        conditions.append(f"no_building = ${param_idx}")
        params.append(no_building)
        param_idx += 1

    if exclude_alr:
        conditions.append("in_alr = FALSE")

    where_clause = " AND ".join(conditions)
    query = f"""
        SELECT
            id, pid, civic_address, owner_name, lot_area_sqm, owner_type,
            zone_code, zone_description, permits_assembly, max_far,
            land_value, improvement_value, total_value,
            no_building, in_alr, flood_hazard_level,
            dist_to_canada_line_m,
            mls_number, list_price, listing_status,
            ST_AsGeoJSON(ST_Simplify(geom, 0.00001))::json AS geojson,
            COUNT(*) OVER() AS total_count
        FROM enriched_parcels
        WHERE {where_clause}
        LIMIT ${param_idx}
    """  # noqa: S608
    params.append(limit)

    pool = await get_pool()
    rows = await pool.fetch(query, *params)

    features = []
    total_count = 0
    for row in rows:
        total_count = row["total_count"]
        geojson = row["geojson"] if isinstance(row["geojson"], dict) else json.loads(row["geojson"])
        features.append(
            GeoJSONFeature(
                geometry=geojson,
                properties=ParcelProperties(
                    id=row["id"],
                    pid=row["pid"],
                    civic_address=row["civic_address"],
                    owner_name=row["owner_name"],
                    lot_area_sqm=float(row["lot_area_sqm"]) if row["lot_area_sqm"] else None,
                    owner_type=row["owner_type"],
                    zone_code=row["zone_code"],
                    zone_description=row["zone_description"],
                    permits_assembly=row["permits_assembly"],
                    max_far=float(row["max_far"]) if row["max_far"] else None,
                    land_value=float(row["land_value"]) if row["land_value"] else None,
                    improvement_value=float(row["improvement_value"]) if row["improvement_value"] else None,
                    total_value=float(row["total_value"]) if row["total_value"] else None,
                    no_building=row["no_building"],
                    in_alr=row["in_alr"],
                    flood_hazard_level=row["flood_hazard_level"],
                    dist_to_canada_line_m=(
                        float(row["dist_to_canada_line_m"]) if row["dist_to_canada_line_m"] else None
                    ),
                    mls_number=row["mls_number"],
                    list_price=float(row["list_price"]) if row["list_price"] else None,
                    listing_status=row["listing_status"],
                ),
            )
        )

    return ParcelCollection(type="FeatureCollection", features=features, total_count=total_count)
