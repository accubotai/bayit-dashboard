-- Migration 002: Create core tables
-- All geometry columns use EPSG:4326 (WGS84)

-- Parcels (GeoHub + ParcelMap BC)
CREATE TABLE IF NOT EXISTS parcels (
    id SERIAL PRIMARY KEY,
    pid VARCHAR(12) UNIQUE,
    civic_address TEXT,
    owner_name TEXT,
    lot_area_sqm NUMERIC,
    geom GEOMETRY(MultiPolygon, 4326),
    source VARCHAR(20),
    owner_type VARCHAR(20),
    last_synced TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parcels_geom ON parcels USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_parcels_pid ON parcels (pid);
CREATE INDEX IF NOT EXISTS idx_parcels_owner ON parcels (owner_type);

-- Zoning Districts
CREATE TABLE IF NOT EXISTS zoning_districts (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(20),
    zone_description TEXT,
    permits_assembly BOOLEAN DEFAULT FALSE,
    max_far NUMERIC,
    max_height_m NUMERIC,
    geom GEOMETRY(MultiPolygon, 4326),
    last_synced TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zones_geom ON zoning_districts USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_zones_code ON zoning_districts (zone_code);

-- Building Footprints
CREATE TABLE IF NOT EXISTS building_footprints (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326),
    last_synced TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_buildings_geom ON building_footprints USING GIST (geom);

-- MLS Listings (future phase)
CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    mls_number VARCHAR(20) UNIQUE,
    address TEXT,
    normalized_address TEXT,
    list_price NUMERIC,
    property_type VARCHAR(50),
    lot_size_sqm NUMERIC,
    bedrooms INT,
    bathrooms INT,
    days_on_market INT,
    listing_status VARCHAR(20),
    listing_agent TEXT,
    listing_brokerage TEXT,
    mls_zoning TEXT,
    lat NUMERIC,
    lng NUMERIC,
    geom GEOMETRY(Point, 4326),
    matched_parcel_pid VARCHAR(12),
    last_synced TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listings_geom ON listings USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_listings_parcel ON listings (matched_parcel_pid);

-- BC Assessment data
CREATE TABLE IF NOT EXISTS assessments (
    id SERIAL PRIMARY KEY,
    pid VARCHAR(12) UNIQUE,
    roll_number VARCHAR(20),
    owner_name TEXT,
    property_class_code INT,
    actual_use_code VARCHAR(10),
    land_value NUMERIC,
    improvement_value NUMERIC,
    total_value NUMERIC,
    is_exempt BOOLEAN DEFAULT FALSE,
    exempt_type TEXT,
    assessment_year INT,
    last_synced TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assessments_pid ON assessments (pid);

-- ALR Boundary (Agricultural Land Reserve)
CREATE TABLE IF NOT EXISTS alr_boundary (
    id SERIAL PRIMARY KEY,
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_alr_geom ON alr_boundary USING GIST (geom);

-- Flood Hazard Areas
CREATE TABLE IF NOT EXISTS flood_hazard (
    id SERIAL PRIMARY KEY,
    hazard_level VARCHAR(20),
    geom GEOMETRY(MultiPolygon, 4326)
);

CREATE INDEX IF NOT EXISTS idx_flood_geom ON flood_hazard USING GIST (geom);

-- Transit Stops (TransLink GTFS)
CREATE TABLE IF NOT EXISTS transit_stops (
    id SERIAL PRIMARY KEY,
    stop_name TEXT,
    route_type INT,
    lat NUMERIC,
    lng NUMERIC,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_transit_geom ON transit_stops USING GIST (geom);
