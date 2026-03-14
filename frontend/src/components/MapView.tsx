import { useState, useCallback, useEffect } from 'react';
import Map, { Source, Layer, Popup } from 'react-map-gl/maplibre';
import type { MapLayerMouseEvent } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

import { useParcels } from '../hooks/useParcels';
import { useFilters } from '../hooks/useFilters';
import { useMapViewport } from '../hooks/useMapViewport';
import { FilterPanel } from './FilterPanel';
import { DetailPanel } from './DetailPanel';
import { ParcelPopup } from './ParcelPopup';
import type { ParcelProperties, GeoJSONFeature } from '../utils/api';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json';

// Color parcels by owner type
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const FILL_COLOR: any = [
  'case',
  ['==', ['get', 'owner_type'], 'Municipal'], '#3b82f6',
  ['==', ['get', 'owner_type'], 'Crown Provincial'], '#8b5cf6',
  '#9ca3af',
];

export function MapView() {
  const { mapRef, viewState, setViewState, bbox, onMoveEnd } = useMapViewport();
  const { filters, updateFilter, resetFilters } = useFilters();
  const { data, isLoading, error } = useParcels(bbox, filters);

  const [popupFeature, setPopupFeature] = useState<GeoJSONFeature | null>(null);
  const [popupLngLat, setPopupLngLat] = useState<[number, number] | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<ParcelProperties | null>(null);

  useEffect(() => {
    const timer = setTimeout(onMoveEnd, 500);
    return () => clearTimeout(timer);
  }, [onMoveEnd]);

  const onClick = useCallback((e: MapLayerMouseEvent) => {
    const feature = e.features?.[0];
    if (!feature) {
      setPopupFeature(null);
      setPopupLngLat(null);
      return;
    }
    setPopupFeature(feature as unknown as GeoJSONFeature);
    setPopupLngLat([e.lngLat.lng, e.lngLat.lat]);
  }, []);

  // Build strict GeoJSON for MapLibre (no extra keys like total_count)
  const featureCount = data?.features?.length ?? 0;
  const geojsonData = {
    type: 'FeatureCollection' as const,
    features: (data?.features ?? []).map(f => ({
      type: 'Feature' as const,
      geometry: f.geometry,
      properties: { ...f.properties },
    })),
  };

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        onMoveEnd={onMoveEnd}
        onClick={onClick}
        interactiveLayerIds={['parcels-fill']}
        mapStyle={MAP_STYLE}
        style={{ width: '100%', height: '100%' }}
      >
        <Source id="parcels" type="geojson" data={geojsonData}>
          <Layer
            id="parcels-fill"
            type="fill"
            paint={{
              'fill-color': FILL_COLOR,
              'fill-opacity': 0.6,
            }}
          />
          <Layer
            id="parcels-outline"
            type="line"
            paint={{
              'line-color': '#1e293b',
              'line-width': 1,
              'line-opacity': 0.8,
            }}
          />
        </Source>

        {popupFeature && popupLngLat && (
          <Popup
            longitude={popupLngLat[0]}
            latitude={popupLngLat[1]}
            onClose={() => { setPopupFeature(null); setPopupLngLat(null); }}
            closeButton
            closeOnClick={false}
            maxWidth="280px"
          >
            <ParcelPopup
              parcel={popupFeature.properties}
              onClick={() => {
                setSelectedParcel(popupFeature.properties);
                setPopupFeature(null);
                setPopupLngLat(null);
              }}
            />
          </Popup>
        )}
      </Map>

      <FilterPanel
        filters={filters}
        updateFilter={updateFilter}
        resetFilters={resetFilters}
        totalCount={data?.total_count || 0}
      />

      {selectedParcel && (
        <DetailPanel
          parcel={selectedParcel}
          onClose={() => setSelectedParcel(null)}
        />
      )}

      {/* Status bar */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 rounded-full px-4 py-2 text-sm shadow">
        {isLoading && <span className="text-gray-600">Loading parcels...</span>}
        {error && <span className="text-red-600">Error: {(error as Error).message}</span>}
        {!isLoading && !error && featureCount > 0 && (
          <span className="text-green-700">{featureCount} parcels loaded ({data?.total_count?.toLocaleString()} total in area)</span>
        )}
        {!isLoading && !error && featureCount === 0 && bbox && (
          <span className="text-gray-500">No parcels in this area. Try panning east.</span>
        )}
      </div>
    </div>
  );
}
