"""No-PHI bounded route metrics and guarded runtime behavior."""
from __future__ import annotations

import json

import pytest

from fastapi.testclient import TestClient

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from packages.telemetry.runtime import LATENCY_BUCKETS, RuntimeTelemetry
from scripts.operational_smoke import _security_headers, _url


def test_metrics_do_not_collect_unknown_urls_or_identifiers() -> None:
    tracker = RuntimeTelemetry(frozenset({"/health", "/items/{item_id}"}))
    tracker.observe("GET", "/health", 200, 0.01)
    tracker.observe("GET", "/items/secret-token?email=someone", 404, 0.1)
    tracker.observe("POST", "/items/{item_id}", 503, 100)
    data = tracker.snapshot()
    assert data["total_requests"] == 3
    assert sum(data["latency_buckets_ms"].values()) == 3
    assert "+Inf" in data["latency_buckets_ms"]
    assert len(LATENCY_BUCKETS) > 0
    flat = json.dumps(data)
    assert "secret-token" not in flat
    assert "someone" not in flat
    assert "<unmatched>" in flat
    assert "/items/{item_id}" in flat


def test_actual_http_middleware_observes_bounded_routes() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/readiness").status_code == 503
        assert client.get("/random/path?identity=secret").status_code == 404
        assert client.get("/api/v1/models/current").status_code == 401
    data = app.state.telemetry.snapshot()
    assert data["total_requests"] == 4
    assert all(x["requests"] >= 1 for x in data["routes"])
    assert any(x["status_family"] == "5xx" for x in data["routes"])
    assert "secret" not in json.dumps(data)
    assert "random/path" not in json.dumps(data)


def test_telemetry_buckets_are_bounded_for_extreme_duration() -> None:
    tracker = RuntimeTelemetry(frozenset({"/safe"}))
    tracker.observe("GET", "/safe", 200, -5)
    tracker.observe("UNEXPECTED-METHOD-WITH-SECRET", "arbitrary", 999, 999999)
    snapshot = tracker.snapshot()
    assert snapshot["latency_buckets_ms"]["50"] == 1
    assert snapshot["latency_buckets_ms"]["+Inf"] == 1
    assert snapshot["routes"][-1]["method"] in {"GET", "OTHER"}
    assert "SECRET" not in json.dumps(snapshot)


def test_smoke_url_and_security_header_guards() -> None:
    assert _url("http://127.0.0.1:8000", "/api/v1/health").endswith("/api/v1/health")
    for base in (
        "http://external.example.org", "https://person:password@example.org",
        "https://example.org/private", "https://example.org?token=secret",
    ):
        with pytest.raises(ValueError):
            _url(base, "/api/v1/health")
    valid = {
        "cache-control": "no-store",
        "x-content-type-options": "nosniff",
        "x-request-id": "00000000-0000-4000-8000-000000000001",
    }
    _security_headers(valid)
    for missing in valid:
        with pytest.raises(AssertionError):
            _security_headers({key: value for key, value in valid.items() if key != missing})
