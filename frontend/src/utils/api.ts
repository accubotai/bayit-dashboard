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
  exclude_alr?: boolean;
  hide_private?: boolean;
  min_lot_area?: number;
}

// Clamp bbox to Richmond bounds so the API doesn't reject it
function clampBbox(bbox: [number, number, number, number]): [number, number, number, number] {
  return [
    Math.max(bbox[0], -123.30),
    Math.max(bbox[1], 49.08),
    Math.min(bbox[2], -123.00),
    Math.min(bbox[3], 49.23),
  ];
}

export async function fetchParcels(
  bbox: [number, number, number, number],
  limit: number = 500,
  filters: Filters = {},
): Promise<ParcelCollection> {
  const clamped = clampBbox(bbox);
  if (clamped[0] >= clamped[2] || clamped[1] >= clamped[3]) {
    return { type: 'FeatureCollection', features: [], total_count: 0 };
  }
  const params = new URLSearchParams({
    bbox: clamped.join(','),
    limit: String(limit),
  });

  if (filters.owner_type) params.set('owner_type', filters.owner_type);
  if (filters.exclude_alr) params.set('exclude_alr', 'true');
  if (filters.hide_private) params.set('hide_private', 'true');
  if (filters.min_lot_area) params.set('min_lot_area', String(filters.min_lot_area));

  const res = await fetch(`${API_BASE}/api/parcels?${params}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
