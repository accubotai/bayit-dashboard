import { useQuery } from '@tanstack/react-query';
import { fetchParcels, type Filters, type ParcelCollection } from '../utils/api';

export function useParcels(
  bbox: [number, number, number, number] | null,
  filters: Filters = {},
) {
  return useQuery<ParcelCollection>({
    queryKey: ['parcels', bbox, filters],
    queryFn: () => fetchParcels(bbox!, 500, filters),
    enabled: bbox !== null,
    staleTime: 30_000,
    refetchOnWindowFocus: false,
  });
}
