import { useState, useCallback } from 'react';
import Map, { Source, Layer, Popup } from 'react-map-gl/maplibre';
import type { MapLayerMouseEvent } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

import { useParcels } from '../hooks/useParcels';
import { useAssemblyParcels } from '../hooks/useAssemblyParcels';
import { useAssemblyFilters } from '../hooks/useAssemblyFilters';
import { useFilters } from '../hooks/useFilters';
import { useMapViewport } from '../hooks/useMapViewport';
import { FilterPanel } from './FilterPanel';
import { DetailPanel } from './DetailPanel';
import { ParcelPopup } from './ParcelPopup';
import { AssemblyPopup } from './AssemblyPopup';
import { AssemblyDetailPanel } from './AssemblyDetailPanel';
import type { ParcelProperties, GeoJSONFeature, AssemblyProperties } from '../utils/api';

const MAP_STYLE = 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json';

// Color parcels by owner type
const FILL_COLOR: unknown = [
  'case',
  ['==', ['get', 'owner_type'], 'Municipal'], '#3b82f6',
  ['==', ['get', 'owner_type'], 'Crown Provincial'], '#8b5cf6',
  '#9ca3af',
];

export function MapView() {
  const { mapRef, viewState, setViewState, bbox, updateBbox } = useMapViewport();
  const { filters, updateFilter, resetFilters } = useFilters();
  const { data, isLoading, error } = useParcels(bbox, filters);

  const [showAssembly, setShowAssembly] = useState(true);
  const { data: assemblyData } = useAssemblyParcels(bbox, showAssembly);
  const { assemblyFilters, updateAssemblyFilter, resetAssemblyFilters, filterFeature } = useAssemblyFilters();

  const [popupFeature, setPopupFeature] = useState<GeoJSONFeature | null>(null);
  const [popupLngLat, setPopupLngLat] = useState<[number, number] | null>(null);
  const [selectedParcel, setSelectedParcel] = useState<ParcelProperties | null>(null);
  const [selectedAssembly, setSelectedAssembly] = useState<AssemblyProperties | null>(null);
  const [assemblyPopupFeature, setAssemblyPopupFeature] = useState<{ properties: AssemblyProperties; lngLat: [number, number] } | null>(null);

  const onClick = useCallback((e: MapLayerMouseEvent) => {
    const feature = e.features?.[0];
    if (!feature) {
      setPopupFeature(null);
      setPopupLngLat(null);
      setAssemblyPopupFeature(null);
      return;
    }

    // Check if it's an assembly layer click
    const layerId = (feature.layer as { id?: string })?.id;
    if (layerId === 'assembly-fill' || layerId === 'assembly-points') {
      setPopupFeature(null);
      setPopupLngLat(null);
      setAssemblyPopupFeature({
        properties: feature.properties as unknown as AssemblyProperties,
        lngLat: [e.lngLat.lng, e.lngLat.lat],
      });
      return;
    }

    setAssemblyPopupFeature(null);
    setPopupFeature(feature as unknown as GeoJSONFeature);
    setPopupLngLat([e.lngLat.lng, e.lngLat.lat]);
  }, []);

  // Build strict GeoJSON for MapLibre
  const featureCount = data?.features?.length ?? 0;
  const geojsonData = {
    type: 'FeatureCollection' as const,
    features: (data?.features ?? []).map(f => ({
      type: 'Feature' as const,
      geometry: f.geometry,
      properties: { ...f.properties },
    })),
  };

  // Assembly parcels — filter, then separate into polygons and points
  const filteredAssembly = (assemblyData?.features ?? []).filter(f => filterFeature(f.properties));
  const assemblyPolygons = {
    type: 'FeatureCollection' as const,
    features: filteredAssembly
      .filter(f => f.properties.geom_type === 'polygon')
      .map(f => ({
        type: 'Feature' as const,
        geometry: f.geometry,
        properties: { ...f.properties },
      })),
  };
  const assemblyPoints = {
    type: 'FeatureCollection' as const,
    features: filteredAssembly
      .filter(f => f.properties.geom_type === 'point')
      .map(f => ({
        type: 'Feature' as const,
        geometry: f.geometry,
        properties: { ...f.properties },
      })),
  };
  const assemblyCount = filteredAssembly.length;
  const assemblyTotalInView = assemblyData?.features?.length ?? 0;

  return (
    <div className="relative w-full h-full">
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt: { viewState: typeof viewState }) => setViewState(evt.viewState)}
        onMoveEnd={updateBbox}
        onLoad={updateBbox}
        onClick={onClick}
        interactiveLayerIds={['parcels-fill', ...(showAssembly ? ['assembly-fill', 'assembly-points'] : [])]}
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

        {/* Assembly-zoned parcels — gold/amber overlay */}
        {showAssembly && (
          <>
            <Source id="assembly-polygons" type="geojson" data={assemblyPolygons}>
              <Layer
                id="assembly-fill"
                type="fill"
                paint={{
                  'fill-color': '#f59e0b',
                  'fill-opacity': 0.55,
                }}
              />
              <Layer
                id="assembly-outline"
                type="line"
                paint={{
                  'line-color': '#b45309',
                  'line-width': 2,
                  'line-opacity': 0.9,
                }}
              />
            </Source>
            <Source id="assembly-points" type="geojson" data={assemblyPoints}>
              <Layer
                id="assembly-points"
                type="circle"
                paint={{
                  'circle-radius': 6,
                  'circle-color': '#f59e0b',
                  'circle-stroke-color': '#b45309',
                  'circle-stroke-width': 2,
                }}
              />
            </Source>
          </>
        )}

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

        {assemblyPopupFeature && (
          <Popup
            longitude={assemblyPopupFeature.lngLat[0]}
            latitude={assemblyPopupFeature.lngLat[1]}
            onClose={() => setAssemblyPopupFeature(null)}
            closeButton
            closeOnClick={false}
            maxWidth="320px"
          >
            <AssemblyPopup
              parcel={assemblyPopupFeature.properties}
              onClick={() => {
                setSelectedAssembly(assemblyPopupFeature.properties);
                setAssemblyPopupFeature(null);
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
        showAssembly={showAssembly}
        onToggleAssembly={() => setShowAssembly(prev => !prev)}
        assemblyCount={assemblyCount}
        assemblyTotalInView={assemblyTotalInView}
        assemblyFilters={assemblyFilters}
        updateAssemblyFilter={updateAssemblyFilter}
        resetAssemblyFilters={resetAssemblyFilters}
      />

      {selectedParcel && (
        <DetailPanel
          parcel={selectedParcel}
          onClose={() => setSelectedParcel(null)}
        />
      )}

      {selectedAssembly && (
        <AssemblyDetailPanel
          parcel={selectedAssembly}
          onClose={() => setSelectedAssembly(null)}
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
          <span className="text-gray-500">No parcels in this area — try panning or zooming.</span>
        )}
        {!isLoading && !error && !bbox && (
          <span className="text-gray-500">Loading map...</span>
        )}
      </div>
    </div>
  );
}
