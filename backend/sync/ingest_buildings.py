"""Building footprints — placeholder until City of Richmond publishes GIS data.

Richmond BC does not expose building footprint polygons via a public API.
Building footprint data would need to be obtained from RIM network inspection
or a future open data release.
"""

from __future__ import annotations


async def ingest_buildings() -> int:
    """Placeholder — building footprint polygons not publicly available.

    Returns 0 (no data source available).
    """
    print("=== Building Footprints ===")
    print("  SKIPPED: Richmond BC building footprints not publicly available via API.")
    return 0
