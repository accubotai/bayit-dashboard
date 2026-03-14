"""Zoning districts — placeholder until City of Richmond publishes GIS data.

Richmond BC does not expose zoning district polygons via a public API.
The zone_use_permissions lookup table is seeded in migration 003.
Zoning spatial data would need to be obtained from RIM (Richmond Interactive Map)
network inspection or a future open data release.
"""

from __future__ import annotations


async def ingest_zones() -> int:
    """Placeholder — zoning district polygons not publicly available.

    Returns 0 (no data source available).
    """
    print("=== Zoning Districts ===")
    print("  SKIPPED: Richmond BC zoning polygons not publicly available via API.")
    print("  Zone use permissions are seeded via SQL migration 003.")
    return 0
