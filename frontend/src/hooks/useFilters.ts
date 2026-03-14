import { useState, useCallback } from 'react';
import type { Filters } from '../utils/api';

export function useFilters() {
  const [filters, setFilters] = useState<Filters>({});

  const updateFilter = useCallback(<K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters(prev => {
      const next = { ...prev };
      if (value === undefined || value === '' || value === false) {
        delete next[key];
      } else {
        next[key] = value;
      }
      return next;
    });
  }, []);

  const resetFilters = useCallback(() => setFilters({}), []);

  return { filters, updateFilter, resetFilters };
}
