"""Data source URLs and database connection config for ingestion scripts."""

from __future__ import annotations

import os

# BC Data Catalogue — ParcelMap BC (WFS, public, OGL-BC license)
BC_PARCELS_WFS_URL = os.getenv(
    "BC_PARCELS_WFS_URL",
    "https://openmaps.gov.bc.ca/geo/pub/ows",
)
BC_PARCELS_LAYER = "pub:WHSE_CADASTRE.PMBC_PARCEL_FABRIC_POLY_SVW"
RICHMOND_MUNICIPALITY = "Richmond, City of"

# BC Data Catalogue — ALR boundary (WFS)
ALR_WFS_URL = os.getenv(
    "ALR_WFS_URL",
    "https://openmaps.gov.bc.ca/geo/pub/ows",
)
ALR_LAYER = "pub:WHSE_LEGAL_ADMIN_BOUNDARIES.OATS_ALR_POLYS"

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

# Richmond bounding box (EPSG:4326) — covers full City of Richmond
RICHMOND_BBOX = {
    "xmin": -123.30,
    "ymin": 49.08,
    "xmax": -123.00,
    "ymax": 49.23,
}

# WFS fetch limit per request (BC WFS caps at 10,000)
WFS_MAX_FEATURES = 10000

# Grid subdivision for fetching all parcels (cols x rows tiles)
# 10x5 = 50 tiles ensures no single tile exceeds the 10k WFS cap
WFS_GRID_COLS = 10
WFS_GRID_ROWS = 5
