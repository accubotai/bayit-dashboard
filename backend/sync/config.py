"""Data source URLs and database connection config for ingestion scripts."""

from __future__ import annotations

import os

# Richmond GeoHub ArcGIS REST API endpoints
# Find the actual FeatureServer URL by going to the GeoHub dataset page,
# clicking "I want to use this" → "View API resources" → copy FeatureServer URL.
GEOHUB_PARCELS_URL = os.getenv(
    "GEOHUB_PARCELS_URL",
    "https://services2.arcgis.com/DBVMRhKBTxLSFj6u/arcgis/rest/services/Parcels/FeatureServer/0/query",
)

GEOHUB_ZONING_URL = os.getenv(
    "GEOHUB_ZONING_URL",
    "https://services2.arcgis.com/DBVMRhKBTxLSFj6u/arcgis/rest/services/Zoning_Districts/FeatureServer/0/query",
)

GEOHUB_BUILDINGS_URL = os.getenv(
    "GEOHUB_BUILDINGS_URL",
    "https://services2.arcgis.com/DBVMRhKBTxLSFj6u/arcgis/rest/services/Building_Footprints/FeatureServer/0/query",
)

# BC Data Catalogue — ALR boundary (WFS)
ALR_WFS_URL = os.getenv(
    "ALR_WFS_URL",
    "https://openmaps.gov.bc.ca/geo/pub/ows",
)

# TransLink GTFS static feed
TRANSLINK_GTFS_URL = os.getenv(
    "TRANSLINK_GTFS_URL",
    "https://gtfs-static.translink.ca/gtfs/google_transit.zip",
)

# Database connection (direct, not pooled — for bulk inserts)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "SUPABASE_DIRECT_URL",
        "postgresql://user:password@localhost:5432/richmond_land",
    ),
)

# Richmond bounding box for spatial filters
RICHMOND_BBOX = {
    "xmin": -123.30,
    "ymin": 49.10,
    "xmax": -123.00,
    "ymax": 49.22,
}

# ArcGIS pagination
ARCGIS_PAGE_SIZE = 1000
