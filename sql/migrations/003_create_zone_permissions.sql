-- Migration 003: Zone use permissions lookup
-- Tracks which Richmond zone codes permit specific uses (assembly, etc.)
-- Based on Richmond Zoning Bylaw 8500

CREATE TABLE IF NOT EXISTS zone_use_permissions (
    id SERIAL PRIMARY KEY,
    zone_code VARCHAR(20) NOT NULL,
    use_category VARCHAR(50) NOT NULL,
    permission_type VARCHAR(20) NOT NULL
        CHECK (permission_type IN ('permitted', 'conditional', 'prohibited')),
    notes TEXT,
    bylaw_reference TEXT
);

CREATE INDEX IF NOT EXISTS idx_zone_perms_code ON zone_use_permissions (zone_code);
CREATE INDEX IF NOT EXISTS idx_zone_perms_use ON zone_use_permissions (use_category);

-- Seed assembly-use permissions from Bylaw 8500
INSERT INTO zone_use_permissions (zone_code, use_category, permission_type, notes, bylaw_reference) VALUES
    ('AG1', 'assembly', 'prohibited', 'Agricultural — no assembly use', 'Bylaw 8500'),
    ('AG2', 'assembly', 'prohibited', 'Agricultural — no assembly use', 'Bylaw 8500'),
    ('RS1', 'assembly', 'prohibited', 'Single-family residential — no assembly', 'Bylaw 8500'),
    ('RS2', 'assembly', 'prohibited', 'Single-family residential — no assembly', 'Bylaw 8500'),
    ('RC1', 'assembly', 'prohibited', 'Compact lot residential — no assembly', 'Bylaw 8500'),
    ('RC2', 'assembly', 'prohibited', 'Compact lot residential — no assembly', 'Bylaw 8500'),
    ('RM1', 'assembly', 'conditional', 'Low-density multifamily — conditional assembly', 'Bylaw 8500'),
    ('RM2', 'assembly', 'conditional', 'Medium-density multifamily — conditional assembly', 'Bylaw 8500'),
    ('RM3', 'assembly', 'conditional', 'High-density multifamily — conditional assembly', 'Bylaw 8500'),
    ('RM4', 'assembly', 'conditional', 'High-density multifamily — conditional assembly', 'Bylaw 8500'),
    ('C1', 'assembly', 'permitted', 'Local commercial — assembly permitted', 'Bylaw 8500'),
    ('C2', 'assembly', 'permitted', 'General commercial — assembly permitted', 'Bylaw 8500'),
    ('C3', 'assembly', 'permitted', 'Community commercial — assembly permitted', 'Bylaw 8500'),
    ('C4', 'assembly', 'permitted', 'Highway commercial — assembly permitted', 'Bylaw 8500'),
    ('C5', 'assembly', 'permitted', 'Auto-oriented commercial — assembly permitted', 'Bylaw 8500'),
    ('C6', 'assembly', 'permitted', 'Service commercial — assembly permitted', 'Bylaw 8500'),
    ('CS1', 'assembly', 'permitted', 'Community service — assembly permitted', 'Bylaw 8500'),
    ('I1', 'assembly', 'prohibited', 'Industrial — no assembly', 'Bylaw 8500'),
    ('I2', 'assembly', 'prohibited', 'Industrial — no assembly', 'Bylaw 8500'),
    ('CDT1', 'assembly', 'permitted', 'City centre district — assembly permitted', 'Bylaw 8500'),
    ('ZMU', 'assembly', 'permitted', 'Mixed use — assembly permitted', 'Bylaw 8500'),
    ('ZC', 'assembly', 'permitted', 'Comprehensive development — assembly permitted', 'Bylaw 8500'),
    ('PA1', 'assembly', 'permitted', 'Public and institutional — assembly permitted', 'Bylaw 8500'),
    ('PA2', 'assembly', 'permitted', 'Public and institutional — assembly permitted', 'Bylaw 8500')
ON CONFLICT DO NOTHING;
