"""Parcels API endpoint — returns enriched parcels as GeoJSON."""

from __future__ import annotations

import json
import logging

import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.config import validate_bbox
from backend.db import SUPABASE_KEY, SUPABASE_URL, get_pool, use_rest
from backend.models import GeoJSONFeature, ParcelCollection, ParcelProperties

logger = logging.getLogger(__name__)

router = APIRouter(tags=["parcels"])


def _row_to_feature(row: dict) -> GeoJSONFeature:
    """Convert a database row to a GeoJSON feature."""
    geojson = row["geojson"]
    if isinstance(geojson, str):
        geojson = json.loads(geojson)

    return GeoJSONFeature(
        geometry=geojson,
        properties=ParcelProperties(
            id=row["id"],
            pid=row.get("pid"),
            civic_address=row.get("civic_address"),
            owner_name=row.get("owner_name"),
            lot_area_sqm=float(row["lot_area_sqm"]) if row.get("lot_area_sqm") else None,
            owner_type=row.get("owner_type"),
            zone_code=row.get("zone_code"),
            zone_description=row.get("zone_description"),
            permits_assembly=row.get("permits_assembly"),
            max_far=float(row["max_far"]) if row.get("max_far") else None,
            land_value=float(row["land_value"]) if row.get("land_value") else None,
            improvement_value=float(row["improvement_value"]) if row.get("improvement_value") else None,
            total_value=float(row["total_value"]) if row.get("total_value") else None,
            no_building=row.get("no_building"),
            in_alr=row.get("in_alr"),
            flood_hazard_level=row.get("flood_hazard_level"),
            dist_to_canada_line_m=(float(row["dist_to_canada_line_m"]) if row.get("dist_to_canada_line_m") else None),
            mls_number=row.get("mls_number"),
            list_price=float(row["list_price"]) if row.get("list_price") else None,
            listing_status=row.get("listing_status"),
        ),
    )


@router.get("/parcels", response_model=ParcelCollection)
async def get_parcels(
    bbox: str = Query(
        ...,
        description="Bounding box: min_lng,min_lat,max_lng,max_lat",
        pattern=r"^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$",
    ),
    limit: int = Query(500, ge=1, le=2000),
    owner_type: str | None = Query(None, description="Filter by owner type"),
    exclude_alr: bool = Query(False, description="Exclude ALR parcels"),
) -> ParcelCollection:
    """Return enriched parcels within a bounding box as GeoJSON FeatureCollection."""
    parts = bbox.split(",")
    min_lng, min_lat, max_lng, max_lat = (float(p) for p in parts)

    try:
        validate_bbox(min_lng, min_lat, max_lng, max_lat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if use_rest():
        rows = await _fetch_via_rest(min_lng, min_lat, max_lng, max_lat, limit, owner_type, exclude_alr)
    else:
        rows = await _fetch_via_asyncpg(min_lng, min_lat, max_lng, max_lat, limit, owner_type, exclude_alr)

    features = [_row_to_feature(row) for row in rows]
    total_count = int(rows[0]["total_count"]) if rows else 0

    return ParcelCollection(type="FeatureCollection", features=features, total_count=total_count)


async def _fetch_via_rest(
    min_lng: float,
    min_lat: float,
    max_lng: float,
    max_lat: float,
    limit: int,
    owner_type: str | None,
    exclude_alr: bool,
) -> list[dict]:
    """Fetch parcels via Supabase RPC (PostgREST)."""
    rpc_params = {
        "min_lng": min_lng,
        "min_lat": min_lat,
        "max_lng": max_lng,
        "max_lat": max_lat,
        "p_limit": limit,
        "p_owner_type": owner_type,
        "p_exclude_alr": exclude_alr,
    }
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=9.0) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/get_parcels_in_bbox",
            headers=headers,
            json=rpc_params,
        )
        if resp.status_code != 200:
            logger.error("Supabase RPC error: %s %s", resp.status_code, resp.text[:200])
            raise HTTPException(status_code=502, detail="Database query failed")
        return resp.json()


async def _fetch_via_asyncpg(
    min_lng: float,
    min_lat: float,
    max_lng: float,
    max_lat: float,
    limit: int,
    owner_type: str | None,
    exclude_alr: bool,
) -> list[dict]:
    """Fetch parcels via asyncpg (local dev)."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM get_parcels_in_bbox($1, $2, $3, $4, $5, $6, $7)",
        min_lng,
        min_lat,
        max_lng,
        max_lat,
        limit,
        owner_type,
        exclude_alr,
    )
    return [dict(row) for row in rows]
