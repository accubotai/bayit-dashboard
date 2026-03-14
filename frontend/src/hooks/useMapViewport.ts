import { useState, useCallback, useRef } from 'react';

// Central Richmond — No. 3 Road corridor, Brighouse area
const INITIAL_VIEW = {
  longitude: -123.137,
  latitude: 49.166,
  zoom: 14,
};

export function useMapViewport() {
  // Use any type for ref since MapLibre types differ from declaration
  const mapRef = useRef<any>(null);
  const [viewState, setViewState] = useState(INITIAL_VIEW);
  const [bbox, setBbox] = useState<[number, number, number, number] | null>(null);

  const updateBbox = useCallback(() => {
    try {
      const map = mapRef.current;
      if (!map) return;
      const mapInstance = map.getMap?.() ?? map;
      const bounds = mapInstance.getBounds?.();
      if (!bounds) return;
      setBbox([
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth(),
      ]);
    } catch {
      // Map not ready yet
    }
  }, []);

  return { mapRef, viewState, setViewState, bbox, updateBbox };
}
