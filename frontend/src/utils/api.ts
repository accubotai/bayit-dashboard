const API_BASE = import.meta.env.VITE_API_URL || '';

export interface ParcelProperties {
  id: number;
  pid: string | null;
  civic_address: string | null;
  owner_name: string | null;
  lot_area_sqm: number | null;
  owner_type: string | null;
  zone_code: string | null;
  zone_description: string | null;
  permits_assembly: boolean | null;
  max_far: number | null;
  land_value: number | null;
  improvement_value: number | null;
  total_value: number | null;
  no_building: boolean | null;
  in_alr: boolean | null;
  flood_hazard_level: string | null;
  dist_to_canada_line_m: number | null;
  mls_number: string | null;
  list_price: number | null;
  listing_status: string | null;
}

export interface GeoJSONFeature {
  type: 'Feature';
  geometry: Record<string, unknown>;
  properties: ParcelProperties;
}

export interface ParcelCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
  total_count: number;
}

export interface Filters {
  owner_type?: string;
  permits_assembly?: boolean;
  no_building?: boolean;
  exclude_alr?: boolean;
}

export async function fetchParcels(
  bbox: [number, number, number, number],
  limit: number = 500,
  filters: Filters = {},
): Promise<ParcelCollection> {
  const params = new URLSearchParams({
    bbox: bbox.join(','),
    limit: String(limit),
  });

  if (filters.owner_type) params.set('owner_type', filters.owner_type);
  if (filters.permits_assembly !== undefined) params.set('permits_assembly', String(filters.permits_assembly));
  if (filters.no_building !== undefined) params.set('no_building', String(filters.no_building));
  if (filters.exclude_alr) params.set('exclude_alr', 'true');

  const res = await fetch(`${API_BASE}/api/parcels?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
