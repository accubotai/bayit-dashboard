import { useState, useCallback } from 'react';
import type { AssemblyProperties } from '../utils/api';

export interface AssemblyFilters {
  excludeAlr: boolean;
  zoning: string;
  ownerType: string;
  minLotArea: number | undefined;
  maxLotArea: number | undefined;
  excludeOccupied: boolean;
  onlyMatched: boolean;
}

// Occupied place types — places with existing structures that can't easily be redeveloped
const OCCUPIED_TYPES = new Set([
  'apartments', 'house', 'residential', 'retail', 'restaurant', 'hotel',
  'commercial', 'school', 'cafe', 'supermarket', 'kindergarten', 'car',
  'alcohol', 'place_of_worship', 'hospital', 'clinic', 'library',
  'bank', 'pharmacy', 'fast_food', 'fuel', 'police', 'fire_station',
]);

const DEFAULTS: AssemblyFilters = {
  excludeAlr: true,
  zoning: '',
  ownerType: '',
  minLotArea: 1000,
  maxLotArea: 50000,
  excludeOccupied: false,
  onlyMatched: false,
};

export function useAssemblyFilters() {
  const [filters, setFilters] = useState<AssemblyFilters>(DEFAULTS);

  const updateFilter = useCallback(<K extends keyof AssemblyFilters>(key: K, value: AssemblyFilters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => setFilters(DEFAULTS), []);

  const filterFeature = useCallback((props: AssemblyProperties): boolean => {
    // ALR filter (only applicable to matched parcels with ALR data)
    if (filters.excludeAlr && props.in_alr) return false;

    // Zoning filter
    if (filters.zoning && props.zoning) {
      if (!props.zoning.includes(filters.zoning)) return false;
    }

    // Owner type filter
    if (filters.ownerType && props.owner_type !== filters.ownerType) return false;

    // Lot area filters (exclude parcels without area data when filter is active)
    if (filters.minLotArea !== undefined) {
      if (props.lot_area_sqm === null || props.lot_area_sqm < filters.minLotArea) return false;
    }
    if (filters.maxLotArea !== undefined) {
      if (props.lot_area_sqm === null || props.lot_area_sqm > filters.maxLotArea) return false;
    }

    // Exclude occupied (based on place_type)
    if (filters.excludeOccupied && props.place_type) {
      if (OCCUPIED_TYPES.has(props.place_type)) return false;
    }

    // Only matched parcels (polygon, not point-only)
    if (filters.onlyMatched && props.geom_type !== 'polygon') return false;

    return true;
  }, [filters]);

  return { assemblyFilters: filters, updateAssemblyFilter: updateFilter, resetAssemblyFilters: resetFilters, filterFeature };
}

// Zone code groups for the dropdown
export const ZONE_GROUPS = [
  { value: '', label: 'All zones' },
  { value: 'ASY', label: 'ASY — Assembly (primary)' },
  { value: 'CA', label: 'CA — Commercial Activity' },
  { value: 'CDT1', label: 'CDT1 — City Centre' },
  { value: 'CC', label: 'CC — Community Commercial' },
  { value: 'CEA', label: 'CEA — Entertainment Area' },
] as const;

// Owner types for the dropdown
export const ASSEMBLY_OWNER_TYPES = [
  { value: '', label: 'All owners' },
  { value: 'Local Government', label: 'Local Government (City)' },
  { value: 'Private', label: 'Private' },
  { value: 'Crown Agency', label: 'Crown Agency' },
  { value: 'Federal', label: 'Federal' },
] as const;
