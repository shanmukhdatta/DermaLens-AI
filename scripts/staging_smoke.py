"""External engineering-only smoke tests; never send a real image or clinical data."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import UUID


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: bytes


def safe_base(base: str) -> str:
    parsed = urlsplit(base)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("Specify a URL origin, not a URL containing credentials or a path")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Remote staging probes require HTTPS")
    return base.rstrip("/")


def fetch(base: str, route: str) -> Response:
    request = Request(safe_base(base) + route, method="GET")
    try:
        response = urlopen(request, timeout=10)  # noqa: S310
    except HTTPError as exc:
        response = exc
    with response:
        return Response(
            status=response.status,
            headers={key.lower(): value for key, value in response.headers.items()},
            body=response.read(65536),
        )


def assess_engineering_response(route: str, response: Response) -> None:
    """Engineering staging assumes inference is unavailable and will not diagnose."""
    expected = {
        "/api/v1/health": (200, {"status": "ok"}),
        "/api/v1/readiness": (503, {"status": "not_ready"}),
    }
    if route in expected:
        status, body = expected[route]
        if response.status != status or json.loads(response.body) != body:
            raise AssertionError(f"Unhealthy engineering API response at {route}")
    elif route == "/api/v1/models/current":
        if response.status != 401:
            raise AssertionError("Unverified model metadata was exposed")
    elif route == "/api/v1/analyses":
        if response.status != 404:
            raise AssertionError("Unvalidated analysis endpoint is unexpectedly exposed")
    else:
        raise ValueError("Unsupported smoke-test route")
    if (
        response.headers.get("cache-control") != "no-store"
        or response.headers.get("x-content-type-options") != "nosniff"
    ):
        raise AssertionError("Missing API privacy/security headers")
    UUID(response.headers["x-request-id"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base-url", default="http://localhost:8000")
    args = parser.parse_args()
    base = safe_base(args.api_base_url)
    for route in (
        "/api/v1/health",
        "/api/v1/readiness",
        "/api/v1/models/current",
        "/api/v1/analyses",
    ):
        assess_engineering_response(route, fetch(base, route))
        print(f"OK: {route}")
    print("Engineering safety smoke passed. This is NOT clinical model or deployment approval.")


if __name__ == "__main__":
    main()
