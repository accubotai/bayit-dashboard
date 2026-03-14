"""Tests for the parcels endpoint — validates input validation without DB."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_parcels_missing_bbox(client: TestClient) -> None:
    """Parcels endpoint requires bbox parameter."""
    response = client.get("/api/parcels")
    assert response.status_code == 422


def test_parcels_invalid_bbox_format(client: TestClient) -> None:
    """Parcels endpoint rejects malformed bbox."""
    response = client.get("/api/parcels?bbox=invalid")
    assert response.status_code == 422


def test_parcels_bbox_outside_richmond(client: TestClient) -> None:
    """Parcels endpoint rejects bbox outside Richmond bounds."""
    response = client.get("/api/parcels?bbox=-130.0,50.0,-129.0,51.0")
    assert response.status_code == 400
    assert "outside Richmond bounds" in response.json()["detail"]


def test_parcels_invalid_limit(client: TestClient) -> None:
    """Parcels endpoint rejects limit > 2000."""
    response = client.get("/api/parcels?bbox=-123.17,49.15,-123.10,49.19&limit=5000")
    assert response.status_code == 422
