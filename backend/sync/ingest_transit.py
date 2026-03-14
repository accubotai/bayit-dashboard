"""Ingest transit stops from TransLink GTFS static feed."""

from __future__ import annotations

import csv
import io
import zipfile

import requests
from backend.sync.config import DATABASE_URL, RICHMOND_BBOX, TRANSLINK_GTFS_URL
from backend.sync.utils import get_db_connection


async def ingest_transit() -> int:
    """Fetch TransLink GTFS feed and extract stops within Richmond bounds.

    Route types: 1 = Rail (Canada Line/SkyTrain), 3 = Bus
    Returns the number of records inserted.
    """
    print("=== Ingesting Transit Stops ===")

    print(f"  Downloading GTFS from {TRANSLINK_GTFS_URL}...")
    resp = requests.get(TRANSLINK_GTFS_URL, timeout=120)
    resp.raise_for_status()

    bbox = RICHMOND_BBOX
    stops: list[dict] = []

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        # Read routes to map route_id → route_type
        route_types: dict[str, int] = {}
        with zf.open("routes.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                route_types[row["route_id"]] = int(row["route_type"])

        # Read trips to map trip_id → route_id
        trip_routes: dict[str, str] = {}
        with zf.open("trips.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                trip_routes[row["trip_id"]] = row["route_id"]

        # Read stop_times to map stop_id → set of route_ids
        stop_route_ids: dict[str, set[str]] = {}
        with zf.open("stop_times.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                stop_id = row["stop_id"]
                trip_id = row["trip_id"]
                if trip_id in trip_routes:
                    if stop_id not in stop_route_ids:
                        stop_route_ids[stop_id] = set()
                    stop_route_ids[stop_id].add(trip_routes[trip_id])

        # Read stops and filter to Richmond bbox
        with zf.open("stops.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))
            for row in reader:
                lat = float(row["stop_lat"])
                lng = float(row["stop_lon"])

                # Filter to Richmond area
                if not (bbox["ymin"] <= lat <= bbox["ymax"] and bbox["xmin"] <= lng <= bbox["xmax"]):
                    continue

                stop_id = row["stop_id"]

                # Determine route type — prefer rail (1) if any rail route serves this stop
                route_type = 3  # default to bus
                if stop_id in stop_route_ids:
                    for rid in stop_route_ids[stop_id]:
                        if route_types.get(rid) == 1:
                            route_type = 1
                            break

                stops.append(
                    {
                        "stop_name": row["stop_name"],
                        "route_type": route_type,
                        "lat": lat,
                        "lng": lng,
                    }
                )

    print(f"  Richmond transit stops found: {len(stops)}")

    conn = await get_db_connection(DATABASE_URL)
    count = 0

    try:
        await conn.execute("TRUNCATE TABLE transit_stops RESTART IDENTITY")

        for stop in stops:
            await conn.execute(
                """
                INSERT INTO transit_stops (stop_name, route_type, lat, lng, geom)
                VALUES ($1, $2, $3, $4, ST_SetSRID(ST_MakePoint($4, $3), 4326))
                """,
                stop["stop_name"],
                stop["route_type"],
                stop["lat"],
                stop["lng"],
            )
            count += 1

    finally:
        await conn.close()

    print(f"  Transit stops ingested: {count}")
    return count
