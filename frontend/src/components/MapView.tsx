import { useState, useCallback, useEffect } from 'react';
import Map, { Source, Layer, Popup } from 'react-map-gl/mapbox';
import type { MapLayerMouseEvent } from 'react-map-gl/mapbox';
import 'mapbox-gl/dist/mapbox-gl.css';

import { useParcels } from '../hooks/useParcels';
import { useFilters } from '../hooks/useFilters';
import { useMapViewport } from '../hooks/useMapViewport';
import { FilterPanel } from './FilterPanel';
import { DetailPanel } from './DetailPanel';
import { ParcelPopup } from './ParcelPopup';
import type { ParcelProperties, GeoJSONFeature } from '../utils/api';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || '';

// Color parcels by type — Mapbox style expression
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const parcelFillColor: any = [
  'case',
  // Municipal vacant = green
  ['all', ['==', ['get', 'owner_type'], 'Municipal'], ['==', ['get', 'no_building'], true]],
  '#22c55e',
  // Municipal with building = blue
  ['==', ['get', 'owner_type'], 'Municipal'],
  '#3b82f6',
  // For sale = orange
  ['!=', ['get', 'mls_number'], null],
  '#f97316',
  // Other = grey
  '#9ca3af',
];

export function MapView() {
  const { mapRef, viewState, setViewState, bbox, onMoveEnd } = useMapViewport();
  const { filters, updateFilter, resetFilters } = useFilters();
  const { data, isLoading } = useParcels(bbox, filters);

  const [popupFeature, setPopupFeature] = useState<GeoJSONFeature | null>(null);
  const [popupLngLat, setPopupLngLat] = useState<[number, number] | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<ParcelProperties | null>(null);

  // Trigger initial load after map renders
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

  const geojson = data || { type: 'FeatureCollection' as const, features: [] };

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        onMoveEnd={onMoveEnd}
        onClick={onClick}
        interactiveLayerIds={['parcels-fill']}
        mapboxAccessToken={MAPBOX_TOKEN}
        mapStyle="mapbox://styles/mapbox/satellite-streets-v12"
        style={{ width: '100%', height: '100%' }}
      >
        <Source id="parcels" type="geojson" data={geojson}>
          <Layer
            id="parcels-fill"
            type="fill"
            paint={{
              'fill-color': parcelFillColor as any,
              'fill-opacity': 0.5,
            }}
          />
          <Layer
            id="parcels-outline"
            type="line"
            paint={{
              'line-color': '#1e293b',
              'line-width': 1,
              'line-opacity': 0.6,
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

      {isLoading && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 rounded-full px-4 py-2 text-sm text-gray-600 shadow">
          Loading parcels...
        </div>
      )}
    </div>
  );
}
