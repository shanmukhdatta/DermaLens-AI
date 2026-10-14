"""Route-level privacy telemetry and engineering smoke assertions without network."""
from __future__ import annotations

import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from scripts.staging_smoke import Response, assess_engineering_response, safe_base


def test_metrics_never_store_query_body_or_actor_details() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        assert client.get("/api/v1/health?secret=private-value").status_code == 200
        assert client.get("/api/v1/readiness").status_code == 503
        assert client.get("/foo/private-user-token").status_code == 404
    observations = app.state.route_metrics.snapshot()
    assert sum(o["requests"] for o in observations) == 3
    assert all(float(o["mean_duration_ms"]) >= 0 for o in observations)
    serialized = json.dumps(observations)
    assert "private-value" not in serialized
    assert "private-user-token" not in serialized
    assert all(x["route"] == "<unmatched>" or x["route"].startswith("/api/v1/") for x in observations)


def _response(status: int, payload: dict[str, str]) -> Response:
    return Response(
        status=status,
        headers={
            "cache-control": "no-store",
            "x-content-type-options": "nosniff",
            "x-request-id": "00000000-0000-4000-8000-000000000001",
        },
        body=json.dumps(payload).encode(),
    )


def test_smoke_validates_fail_closed_engineering() -> None:
    assess_engineering_response("/api/v1/health", _response(200, {"status": "ok"}))
    assess_engineering_response("/api/v1/readiness", _response(503, {"status": "not_ready"}))
    assess_engineering_response("/api/v1/models/current", _response(401, {}))
    assess_engineering_response("/api/v1/analyses", _response(404, {}))
    with pytest.raises(AssertionError):
        assess_engineering_response("/api/v1/readiness", _response(200, {"status": "ok"}))
    with pytest.raises(ValueError):
        safe_base("http://external.example.org")
    with pytest.raises(ValueError):
        safe_base("https://user:secret@example.org")
    assert safe_base("http://localhost:8000/") == "http://localhost:8000"


def test_public_request_id_remains_uuid_and_no_store() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    UUID(response.headers["X-Request-ID"])
    assert response.headers["Cache-Control"] == "no-store"
