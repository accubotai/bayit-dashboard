import { useState, useCallback } from 'react';
import type { Filters } from '../utils/api';

// Default filters for synagogue site search:
// - Hide private land not for sale
// - Exclude ALR (can't build on agricultural land)
// - Minimum 1000 m² lot area (building + parking)
const SYNAGOGUE_DEFAULTS: Filters = {
  hide_private: true,
  exclude_alr: true,
  exclude_unusable: true,
  min_lot_area: 1000,
  max_lot_area: 10000,
};

export function useFilters() {
  const [filters, setFilters] = useState<Filters>(SYNAGOGUE_DEFAULTS);

  const updateFilter = useCallback(<K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  }, []);

  const resetFilters = useCallback(() => setFilters({}), []);

  return { filters, updateFilter, resetFilters };
}
