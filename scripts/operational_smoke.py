"""Black-box local/staging API and web smoke check; no user images or credentials."""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from urllib.parse import urlsplit


def _url(root: str, path: str) -> str:
    parsed = urlsplit(root)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Smoke test base URL must be an explicit HTTP(S) origin")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment or parsed.username:
        raise ValueError("Smoke test base URL must not contain a path or credentials")
    return root.rstrip("/") + path


def _request(root: str, path: str, *, method: str = "GET") -> tuple[int, bytes]:
    request = urllib.request.Request(_url(root, path), method=method)
    try:
        with urllib.request.urlopen(request, timeout=12) as result:
            return result.status, result.read(512 * 1024)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(512 * 1024)


def run(api_origin: str, web_origin: str) -> None:
    """Expect no real classifier and no unverified user's account visibility."""
    code, body = _request(api_origin, "/api/v1/health")
    if code != 200 or json.loads(body) != {"status": "ok"}:
        raise AssertionError("API liveness must be 200 status=ok")
    code, body = _request(api_origin, "/api/v1/readiness")
    if code != 503 or json.loads(body) != {"status": "not_ready"}:
        raise AssertionError("Unvalidated inference readiness must fail closed with 503")
    for target in ("/api/v1/account", "/api/v1/models/current"):
        code, body = _request(api_origin, target)
        if code != 401 or b"NOT_AUTHORIZED" not in body:
            raise AssertionError("Protected API must reject anonymous access")
    code, body = _request(api_origin, "/api/v1/copilot/query", method="POST")
    if code != 404 or b"NOT_FOUND" not in body:
        raise AssertionError("Unconfigured RAG assistant must remain unavailable")
    code, body = _request(web_origin, "/")
    if code != 200 or b"DermaLens" not in body:
        raise AssertionError("Web server must serve the DermaLens landing page")
    print("PASS: local API/web live, safety-gated and account-protected (not clinical readiness).")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-origin", default="http://127.0.0.1:8000")
    parser.add_argument("--web-origin", default="http://127.0.0.1:3000")
    args = parser.parse_args()
    run(args.api_origin, args.web_origin)


if __name__ == "__main__":
    main()
