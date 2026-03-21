-- RPC function: get assembly candidate parcels with their geometries
-- Returns parcel polygons for matched candidates, or point geometries for unmatched

CREATE OR REPLACE FUNCTION get_assembly_parcels(
    min_lng float, min_lat float, max_lng float, max_lat float
)
RETURNS TABLE (
    id integer,
    pid text,
    civic_address text,
    address text,
    zoning text,
    owner_type text,
    lot_area_sqm numeric,
    owner_name text,
    place_type text,
    place_name text,
    in_alr boolean,
    geojson json,
    geom_type text
) LANGUAGE sql STABLE AS $$
    -- Matched candidates: use parcel polygon geometry
    SELECT
        p.id,
        p.pid::text,
        ac.address as civic_address,
        ac.address,
        ac.zoning,
        p.owner_type::text,
        p.lot_area_sqm,
        p.owner_name,
        ac.place_type,
        ac.place_name,
        EXISTS(SELECT 1 FROM alr_boundary a WHERE ST_Intersects(p.geom, a.geom)) as in_alr,
        ST_AsGeoJSON(p.geom)::json as geojson,
        'polygon' as geom_type
    FROM assembly_candidates ac
    JOIN parcels p ON p.id = ac.matched_parcel_id
    WHERE p.geom && ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)

    UNION ALL

    -- Unmatched candidates with coordinates: show as points
    SELECT
        ac.id * -1 as id,  -- negative ID to distinguish from parcels
        ac.matched_pid::text as pid,
        ac.address as civic_address,
        ac.address,
        ac.zoning,
        NULL as owner_type,
        NULL as lot_area_sqm,
        NULL as owner_name,
        ac.place_type,
        ac.place_name,
        false as in_alr,
        ST_AsGeoJSON(ac.geom)::json as geojson,
        'point' as geom_type
    FROM assembly_candidates ac
    WHERE ac.matched_parcel_id IS NULL
      AND ac.geom IS NOT NULL
      AND ac.geom && ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326);
$$;
