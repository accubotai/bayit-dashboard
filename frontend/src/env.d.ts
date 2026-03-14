/// <reference types="vite/client" />

declare module 'react-map-gl/maplibre' {
  import type { ComponentType, RefObject } from 'react';

  export interface MapRef {
    getMap(): {
      getBounds(): {
        getWest(): number;
        getSouth(): number;
        getEast(): number;
        getNorth(): number;
      } | undefined;
    };
  }

  export interface ViewState {
    longitude: number;
    latitude: number;
    zoom: number;
    pitch?: number;
    bearing?: number;
  }

  export interface MapLayerMouseEvent {
    features?: Array<Record<string, unknown>>;
    lngLat: { lng: number; lat: number };
    point: { x: number; y: number };
  }

  export interface MapProps {
    ref?: RefObject<MapRef | null>;
    longitude?: number;
    latitude?: number;
    zoom?: number;
    onMove?: (evt: { viewState: ViewState }) => void;
    onMoveEnd?: () => void;
    onClick?: (e: MapLayerMouseEvent) => void;
    interactiveLayerIds?: string[];
    mapStyle?: string;
    style?: Record<string, string>;
    children?: React.ReactNode;
    [key: string]: unknown;
  }

  const Map: ComponentType<MapProps>;
  export default Map;
  export const Source: ComponentType<{ id: string; type: string; data: unknown; children?: React.ReactNode }>;
  export const Layer: ComponentType<{ id: string; type: string; paint?: Record<string, unknown> }>;
  export const Popup: ComponentType<{
    longitude: number;
    latitude: number;
    onClose: () => void;
    closeButton?: boolean;
    closeOnClick?: boolean;
    maxWidth?: string;
    children?: React.ReactNode;
  }>;
}

declare module 'maplibre-gl/dist/maplibre-gl.css';
