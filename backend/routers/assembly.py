"""Assembly candidates API — parcels zoned for religious assembly."""

from __future__ import annotations

import json
import logging

import httpx
from fastapi import APIRouter, HTTPException, Query

from backend.config import validate_bbox
from backend.db import SUPABASE_KEY, SUPABASE_URL, get_pool, use_rest
from backend.models import AssemblyCollection, AssemblyFeature, AssemblyProperties

logger = logging.getLogger(__name__)

router = APIRouter(tags=["assembly"])


@router.get("/assembly-parcels", response_model=AssemblyCollection)
async def get_assembly_parcels(
    bbox: str = Query(
        ...,
        description="Bounding box: min_lng,min_lat,max_lng,max_lat",
        pattern=r"^-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*,-?\d+\.?\d*$",
    ),
) -> AssemblyCollection:
    """Return assembly-zoned parcels within a bounding box as GeoJSON."""
    parts = bbox.split(",")
    min_lng, min_lat, max_lng, max_lat = (float(p) for p in parts)

    try:
        validate_bbox(min_lng, min_lat, max_lng, max_lat)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    rpc_params = {
        "min_lng": min_lng,
        "min_lat": min_lat,
        "max_lng": max_lng,
        "max_lat": max_lat,
    }

    if use_rest():
        rows = await _fetch_via_rest(rpc_params)
    else:
        rows = await _fetch_via_asyncpg(rpc_params)

    features = []
    for row in rows:
        geojson = row["geojson"]
        if isinstance(geojson, str):
            geojson = json.loads(geojson)

        features.append(
            AssemblyFeature(
                geometry=geojson,
                properties=AssemblyProperties(
                    id=row["id"],
                    pid=row.get("pid"),
                    civic_address=row.get("civic_address"),
                    address=row.get("address"),
                    zoning=row.get("zoning"),
                    owner_type=row.get("owner_type"),
                    lot_area_sqm=float(row["lot_area_sqm"]) if row.get("lot_area_sqm") else None,
                    owner_name=row.get("owner_name"),
                    place_type=row.get("place_type"),
                    place_name=row.get("place_name"),
                    in_alr=row.get("in_alr"),
                    geom_type=row.get("geom_type"),
                ),
            )
        )

    return AssemblyCollection(type="FeatureCollection", features=features, total_count=len(features))


async def _fetch_via_rest(params: dict) -> list[dict]:
    """Fetch via Supabase RPC."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=9.0) as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/get_assembly_parcels",
            headers=headers,
            json=params,
        )
        if resp.status_code != 200:
            logger.error("Supabase RPC error: %s %s", resp.status_code, resp.text[:200])
            raise HTTPException(status_code=502, detail="Database query failed")
        return resp.json()


async def _fetch_via_asyncpg(params: dict) -> list[dict]:
    """Fetch via asyncpg (local dev)."""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM get_assembly_parcels($1, $2, $3, $4)",
        params["min_lng"],
        params["min_lat"],
        params["max_lng"],
        params["max_lat"],
    )
    return [dict(row) for row in rows]
