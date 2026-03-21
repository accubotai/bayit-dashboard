import { useQuery } from '@tanstack/react-query';
import { fetchAssemblyParcels, type AssemblyCollection } from '../utils/api';

export function useAssemblyParcels(
  bbox: [number, number, number, number] | null,
  enabled: boolean = true,
) {
  return useQuery<AssemblyCollection>({
    queryKey: ['assembly-parcels', bbox],
    queryFn: () => fetchAssemblyParcels(bbox!),
    enabled: bbox !== null && enabled,
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });
}
