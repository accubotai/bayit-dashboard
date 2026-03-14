"""Orchestrator script — runs all data ingestion in sequence."""

from __future__ import annotations

import asyncio
import sys
import time

from backend.sync.ingest_alr import ingest_alr
from backend.sync.ingest_buildings import ingest_buildings
from backend.sync.ingest_parcels import ingest_parcels
from backend.sync.ingest_transit import ingest_transit
from backend.sync.ingest_zones import ingest_zones


async def main() -> None:
    """Run all ingestion scripts in sequence."""
    start = time.time()
    print("Starting data ingestion pipeline...\n")

    results: dict[str, int] = {}

    # Order matters: zones needs zone_use_permissions (from migration 003),
    # parcels first since they're the core entity
    steps = [
        ("parcels", ingest_parcels),
        ("zones", ingest_zones),
        ("buildings", ingest_buildings),
        ("alr", ingest_alr),
        ("transit", ingest_transit),
    ]

    for name, func in steps:
        try:
            count = await func()
            results[name] = count
            print()
        except Exception as e:
            print(f"\nERROR ingesting {name}: {e}")
            results[name] = -1

    elapsed = time.time() - start
    print(f"\n{'=' * 50}")
    print("Ingestion Summary:")
    for name, count in results.items():
        status = f"{count} records" if count >= 0 else "FAILED"
        print(f"  {name}: {status}")
    print(f"\nTotal time: {elapsed:.1f}s")

    if any(c < 0 for c in results.values()):
        print("\nSome ingestion steps failed. Check logs above.")
        sys.exit(1)

    print("\nDone. Run 'python scripts/refresh_view.py' to update the materialized view.")


if __name__ == "__main__":
    asyncio.run(main())
