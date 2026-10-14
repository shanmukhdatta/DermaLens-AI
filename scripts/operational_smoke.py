"""Black-box local/staging engineering smoke; never send facial images or credentials."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from uuid import UUID


def _url(root: str, path: str) -> str:
    parsed = urlsplit(root)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Smoke test URL must be an explicit HTTP(S) origin without credentials")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Remote staging smoke tests require HTTPS")
    return root.rstrip("/") + path


def _request(root: str, path: str, *, method: str = "GET") -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(_url(root, path), method=method)
    try:
        response = urllib.request.urlopen(request, timeout=12)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return (
            response.status,
            response.read(512 * 1024),
            {key.lower(): value for key, value in response.headers.items()},
        )


def _security_headers(headers: dict[str, str]) -> None:
    if headers.get("cache-control") != "no-store":
        raise AssertionError("Missing no-store cache privacy header")
    if headers.get("x-content-type-options") != "nosniff":
        raise AssertionError("Missing nosniff header")
    try:
        UUID(headers["x-request-id"])
    except (ValueError, KeyError) as exc:
        raise AssertionError("API response did not contain a valid request correlation ID") from exc


def run(api_origin: str, web_origin: str) -> None:
    """The unvalidated research API must not expose model or user data."""
    code, body, headers = _request(api_origin, "/api/v1/health")
    _security_headers(headers)
    if code != 200 or json.loads(body) != {"status": "ok"}:
        raise AssertionError("API liveness must be 200 status=ok")
    code, body, headers = _request(api_origin, "/api/v1/readiness")
    _security_headers(headers)
    if code != 503 or json.loads(body) != {"status": "not_ready"}:
        raise AssertionError("Unvalidated inference readiness must fail closed with 503")
    for target in ("/api/v1/account", "/api/v1/models/current"):
        code, body, headers = _request(api_origin, target)
        _security_headers(headers)
        if code != 401 or b"NOT_AUTHORIZED" not in body:
            raise AssertionError("Protected API must reject anonymous access")
    for target, method in (
        ("/api/v1/copilot/query", "POST"),
        ("/api/v1/analyses", "GET"),
        ("/api/v1/analyses", "POST"),
    ):
        code, body, headers = _request(api_origin, target, method=method)
        _security_headers(headers)
        if code != 404 or b"NOT_FOUND" not in body:
            raise AssertionError("Unconfigured or unvalidated research feature is exposed")
    code, body, headers = _request(
        api_origin, "/api/v1/docs/search?q=model%20preprocessing"
    )
    _security_headers(headers)
    if code != 200:
        raise AssertionError("Local public documentation search is unavailable")
    lookup = json.loads(body)
    if lookup.get("status") != "matches" or not lookup.get("matches"):
        raise AssertionError("Documentation search yielded no cited project excerpts")
    if "medical_analysis_available" in lookup:
        raise AssertionError("Documentation lookup must never issue medical analysis")
    code, body, _ = _request(web_origin, "/assistant")
    if code != 200 or b"Search project documentation" not in body:
        raise AssertionError("Web server must provide the documentation explorer page")
    code, body, _ = _request(web_origin, "/research")
    if code != 200 or b"Examine independent test results" not in body:
        raise AssertionError("Web server must serve the local research report viewer")
    code, body, _ = _request(web_origin, "/")
    if code != 200 or b"DermaLens" not in body:
        raise AssertionError("Web server must serve the DermaLens landing page")
    print("PASS: API/web live; medical inference unavailable and private routes guarded.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-origin", default="http://127.0.0.1:8000")
    parser.add_argument("--web-origin", default="http://127.0.0.1:3000")
    opts = parser.parse_args()
    run(opts.api_origin, opts.web_origin)


if __name__ == "__main__":
    main()
