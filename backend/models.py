"""Pydantic v2 response models for the API."""

from __future__ import annotations

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    environment: str


class ParcelProperties(BaseModel):
    """Properties for a single parcel GeoJSON feature."""

    id: int
    pid: str | None = None
    civic_address: str | None = None
    owner_name: str | None = None
    lot_area_sqm: float | None = None
    owner_type: str | None = None
    zone_code: str | None = None
    zone_description: str | None = None
    permits_assembly: bool | None = None
    max_far: float | None = None
    land_value: float | None = None
    improvement_value: float | None = None
    total_value: float | None = None
    no_building: bool | None = None
    in_alr: bool | None = None
    flood_hazard_level: str | None = None
    dist_to_canada_line_m: float | None = None
    mls_number: str | None = None
    list_price: float | None = None
    listing_status: str | None = None


class GeoJSONFeature(BaseModel):
    """A single GeoJSON feature."""

    type: str = "Feature"
    geometry: dict
    properties: ParcelProperties


class ParcelCollection(BaseModel):
    """GeoJSON FeatureCollection of parcels."""

    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]
    total_count: int


class ZoneProperties(BaseModel):
    """Properties for a zoning district feature."""

    id: int
    zone_code: str | None = None
    zone_description: str | None = None
    permits_assembly: bool | None = None
    max_far: float | None = None
    max_height_m: float | None = None


class ZoneFeature(BaseModel):
    """A single zoning GeoJSON feature."""

    type: str = "Feature"
    geometry: dict
    properties: ZoneProperties


class ZoneCollection(BaseModel):
    """GeoJSON FeatureCollection of zoning districts."""

    type: str = "FeatureCollection"
    features: list[ZoneFeature]
