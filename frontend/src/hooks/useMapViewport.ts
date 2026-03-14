import { useState, useCallback, useRef } from 'react';
import type { MapRef } from 'react-map-gl/mapbox';

// Central Richmond default view
const INITIAL_VIEW = {
  longitude: -123.135,
  latitude: 49.165,
  zoom: 13,
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
