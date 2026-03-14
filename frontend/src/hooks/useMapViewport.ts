import { useState, useCallback, useRef } from 'react';
import type { MapRef } from 'react-map-gl/maplibre';

// Center on the area where we have parcel data (eastern Richmond)
const INITIAL_VIEW = {
  longitude: -123.03,
  latitude: 49.207,
  zoom: 14,
};

export function useMapViewport() {
  const mapRef = useRef<MapRef>(null);
  const [viewState, setViewState] = useState(INITIAL_VIEW);
  const [bbox, setBbox] = useState<[number, number, number, number] | null>(null);

  const onMoveEnd = useCallback(() => {
    const map = mapRef.current;
    if (!map) return;
    const bounds = map.getMap().getBounds();
    if (!bounds) return;
    setBbox([
      bounds.getWest(),
      bounds.getSouth(),
      bounds.getEast(),
      bounds.getNorth(),
    ]);
  }, []);

  return { mapRef, viewState, setViewState, bbox, onMoveEnd };
}
