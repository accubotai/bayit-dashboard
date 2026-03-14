-- Migration 004: Enriched parcels materialized view
-- Core queryable entity joining parcels with zoning, assessment, vacancy, ALR, flood, transit, and listings

CREATE MATERIALIZED VIEW IF NOT EXISTS enriched_parcels AS
SELECT
    p.id,
    p.pid,
    p.civic_address,
    p.owner_name,
    p.lot_area_sqm,
    p.owner_type,
    p.geom,

    -- Zoning (spatial join via centroid)
    z.zone_code,
    z.zone_description,
    z.permits_assembly,
    z.max_far,

    -- Assessment (PID join)
    a.property_class_code,
    a.actual_use_code,
    a.land_value,
    a.improvement_value,
    a.total_value,
    a.is_exempt,

    -- Vacancy signals
    CASE WHEN bf.id IS NULL THEN TRUE ELSE FALSE END AS no_building,
    CASE WHEN a.improvement_value IS NOT NULL AND a.improvement_value < (a.land_value * 0.1)
         THEN TRUE ELSE FALSE END AS low_improvement_ratio,
    CASE WHEN a.actual_use_code IN ('060', '070', '500', '501')
         THEN TRUE ELSE FALSE END AS bca_vacant,

    -- ALR check
    CASE WHEN alr.id IS NOT NULL THEN TRUE ELSE FALSE END AS in_alr,

    -- Flood hazard
    fh.hazard_level AS flood_hazard_level,

    -- Transit proximity (meters)
    (SELECT MIN(ST_Distance(p.geom::geography, ts.geom::geography))
     FROM transit_stops ts WHERE ts.route_type = 1) AS dist_to_canada_line_m,

    (SELECT MIN(ST_Distance(p.geom::geography, ts.geom::geography))
     FROM transit_stops ts) AS dist_to_any_transit_m,

    -- Active listing (if any)
    l.mls_number,
    l.list_price,
    l.days_on_market,
    l.listing_status

FROM parcels p

LEFT JOIN LATERAL (
    SELECT z2.zone_code, z2.zone_description, z2.permits_assembly, z2.max_far
    FROM zoning_districts z2
    WHERE ST_Intersects(ST_Centroid(p.geom), z2.geom)
    LIMIT 1
) z ON TRUE

LEFT JOIN assessments a ON p.pid = a.pid

LEFT JOIN LATERAL (
    SELECT bf2.id
    FROM building_footprints bf2
    WHERE ST_Intersects(p.geom, bf2.geom)
    LIMIT 1
) bf ON TRUE

LEFT JOIN LATERAL (
    SELECT alr2.id
    FROM alr_boundary alr2
    WHERE ST_Intersects(ST_Centroid(p.geom), alr2.geom)
    LIMIT 1
) alr ON TRUE

LEFT JOIN LATERAL (
    SELECT fh2.hazard_level
    FROM flood_hazard fh2
    WHERE ST_Intersects(ST_Centroid(p.geom), fh2.geom)
    LIMIT 1
) fh ON TRUE

LEFT JOIN LATERAL (
    SELECT l2.mls_number, l2.list_price, l2.days_on_market, l2.listing_status
    FROM listings l2
    WHERE l2.matched_parcel_pid = p.pid
      AND l2.listing_status = 'Active'
    ORDER BY l2.last_synced DESC
    LIMIT 1
) l ON TRUE;

-- Indexes on the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_enriched_id ON enriched_parcels (id);
CREATE INDEX IF NOT EXISTS idx_enriched_geom ON enriched_parcels USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_enriched_zone ON enriched_parcels (zone_code);
CREATE INDEX IF NOT EXISTS idx_enriched_owner ON enriched_parcels (owner_type);
CREATE INDEX IF NOT EXISTS idx_enriched_assembly ON enriched_parcels (permits_assembly);
