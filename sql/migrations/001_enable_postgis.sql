-- Migration 001: Enable PostGIS extension
-- Required for geometry types, spatial indexes, and spatial functions

CREATE EXTENSION IF NOT EXISTS postgis;
