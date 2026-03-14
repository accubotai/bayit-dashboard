"""Orchestrator script — runs all data ingestion in sequence.

Usage:
    uv run python scripts/run_ingest.py              # Full sync (all data)
    uv run python scripts/run_ingest.py --since 2026-03-01  # Incremental (parcels updated since date)
    uv run python scripts/run_ingest.py --parcels-only      # Only parcels
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from backend.sync.ingest_alr import ingest_alr
from backend.sync.ingest_buildings import ingest_buildings
from backend.sync.ingest_parcels import ingest_parcels
from backend.sync.ingest_transit import ingest_transit
from backend.sync.ingest_zones import ingest_zones


async def main() -> None:
    """Run ingestion scripts."""
    parser = argparse.ArgumentParser(description="Bayit Dashboard data ingestion")
    parser.add_argument(
        "--since",
        help="Incremental sync: only fetch parcels updated after this ISO date (e.g. 2026-03-01)",
    )
    parser.add_argument(
        "--parcels-only",
        action="store_true",
        help="Only ingest parcels (skip ALR, transit, etc.)",
    )
    args = parser.parse_args()

    start = time.time()
    mode = f"incremental since {args.since}" if args.since else "full sync"
    print(f"Starting data ingestion pipeline ({mode})...\n")

    results: dict[str, int] = {}

    # Parcels always run
    try:
        count = await ingest_parcels(since=args.since)
        results["parcels"] = count
        print()
    except Exception as e:
        print(f"\nERROR ingesting parcels: {e}")
        results["parcels"] = -1

    # Other sources only on full sync
    if not args.parcels_only:
        other_steps = [
            ("zones", ingest_zones),
            ("buildings", ingest_buildings),
            ("alr", ingest_alr),
            ("transit", ingest_transit),
        ]

        for name, func in other_steps:
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
