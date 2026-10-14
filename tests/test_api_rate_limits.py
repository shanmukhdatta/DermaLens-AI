"""Limit expensive endpoints without retaining raw IP addresses or bypassing proxy headers."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from packages.security.rate_limit import FixedWindowLimiter


def test_buckets_are_independent_and_reset_at_window_boundary() -> None:
    limiter = FixedWindowLimiter(max_identifiers=3, window_seconds=60, secret=b"t" * 32)
    assert limiter.allow("a.b.c.d", "image", limit=2, now=100)
    assert limiter.allow("a.b.c.d", "image", limit=2, now=101)
    assert not limiter.allow("a.b.c.d", "image", limit=2, now=102)
    assert limiter.allow("a.b.c.d", "docs", limit=1, now=103)
    assert not limiter.allow("a.b.c.d", "docs", limit=1, now=104)
    assert limiter.allow("a.b.c.d", "image", limit=2, now=160)
    assert "a.b.c.d" not in json.dumps(limiter._counts)


def test_resource_budgets_fail_closed_if_memory_is_full() -> None:
    limiter = FixedWindowLimiter(max_identifiers=2, secret=b"c" * 32)
    assert limiter.allow("one", "docs", limit=100, now=10)
    assert limiter.allow("two", "image", limit=100, now=10)
    assert not limiter.allow("three", "docs", limit=100, now=10)
    assert limiter.allow("three", "docs", limit=100, now=100)


def test_runtime_returns_safe_429_and_does_not_trust_forwarded_for() -> None:
    app = create_app(Settings(env="test"))
    app.state.request_limiter = FixedWindowLimiter(secret=b"fixture" * 6)
    with TestClient(app, raise_server_exceptions=False) as client:
        for i in range(40):
            response = client.get(
                "/api/v1/docs/search?q=research+pipeline",
                headers={"X-Forwarded-For": f"spoofed-{i}"},
            )
            assert response.status_code == 200
        denied = client.get(
            "/api/v1/docs/search?q=research+pipeline",
            headers={"X-Forwarded-For": "an-untrusted-other-client"},
        )
        assert denied.status_code == 429
        assert denied.json()["error"]["code"] == "RATE_LIMITED"
        assert denied.headers["Cache-Control"] == "no-store"
        assert denied.headers["Retry-After"] == "60"
        assert "spoofed" not in json.dumps(app.state.telemetry.snapshot())


def test_ordinary_health_and_auth_routes_are_not_anonymously_rate_limited() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        for _ in range(50):
            assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/readiness").status_code == 503
        assert client.get("/api/v1/account").status_code == 401
