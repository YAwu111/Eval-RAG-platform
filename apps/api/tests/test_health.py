"""Smoke tests for the HTTP shell: no DB, no models."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app

client = TestClient(create_app())


def test_health_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert body["env"]


def test_unknown_route_uses_error_envelope() -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["details"] is None


def test_openapi_is_exposed() -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"].startswith("TRACE")
