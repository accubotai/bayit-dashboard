-- Migration 005: Assembly candidates — parcels zoned for religious assembly
-- Stores addresses from the "Properties zoned to permit Religious Assembly" CSV
-- with geocoded coordinates and matched parcel IDs.

CREATE TABLE IF NOT EXISTS assembly_candidates (
    id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    zoning TEXT NOT NULL,
    lat NUMERIC,
    lng NUMERIC,
    geom GEOMETRY(Point, 4326),
    matched_parcel_id INTEGER REFERENCES parcels(id),
    matched_pid VARCHAR(12),
    place_type TEXT,          -- what's currently there (from OSM/geocoder)
    place_name TEXT,          -- name of what's there (e.g. "Richmond Centre")
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assembly_geom ON assembly_candidates USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_assembly_parcel ON assembly_candidates (matched_parcel_id);
CREATE INDEX IF NOT EXISTS idx_assembly_address ON assembly_candidates (address);
