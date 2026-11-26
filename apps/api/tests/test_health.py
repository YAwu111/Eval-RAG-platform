"""Smoke tests for the HTTP shell: no DB, no models."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.errors import AppError
from app.main import create_app


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Each test starts from a fresh Settings read."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    # Entering the context runs lifespan startup/shutdown.
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health_contract(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"]
    assert body["db"] == "unknown"
    assert body["models"] == {
        "embedding": "lazy",
        "reranker": "lazy",
        "judges": "lazy",
    }


def test_unknown_route_uses_error_envelope(client: TestClient) -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["details"] is None


def test_method_not_allowed_keeps_allow_header(client: TestClient) -> None:
    response = client.post("/api/health")

    assert response.status_code == 405
    assert response.headers["allow"] == "GET"
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_validation_details_do_not_echo_input() -> None:
    app = create_app()

    @app.get("/api/_test/validate")
    async def validate(n: int) -> dict[str, int]:
        return {"n": n}

    with TestClient(app) as client:
        response = client.get("/api/_test/validate", params={"n": "not-a-number"})

    assert response.status_code == 422
    details = response.json()["error"]["details"]
    assert details[0]["loc"] == ["query", "n"]
    assert "input" not in details[0]


def test_app_error_serializes_datetime_details() -> None:
    app = create_app()

    @app.get("/api/_test/app-error")
    async def app_error() -> None:
        raise AppError(
            "TEAPOT",
            "short and stout",
            status_code=418,
            details={"at": datetime(2026, 11, 26, 12, 0, tzinfo=timezone.utc)},
        )

    with TestClient(app) as client:
        response = client.get("/api/_test/app-error")

    assert response.status_code == 418
    body = response.json()["error"]
    assert body["code"] == "TEAPOT"
    assert body["details"]["at"].startswith("2026-11-26T12:00:00")


def test_500_keeps_envelope_and_cors_header() -> None:
    app = create_app()

    @app.get("/api/_test/crash")
    async def crash() -> None:
        raise RuntimeError("boom")

    # raise_server_exceptions=False lets us assert the wire response.
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/api/_test/crash",
            headers={"Origin": "http://localhost:5173"},
        )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_openapi_is_exposed(client: TestClient) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"].startswith("TRACE")
