"""Request correlation, privacy-minimal access records, and uniform security headers."""

from __future__ import annotations

import json
import logging
import time
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from packages.common.errors import ErrorCode, safe_error_payload

logger = logging.getLogger("dermalens.api")


def request_identifier(header: str | None) -> str:
    """Only canonical UUIDs can be propagated; anything else gets a new server ID."""
    if header is not None:
        try:
            parsed = UUID(header)
            if str(parsed) == header.lower():
                return str(parsed)
        except (ValueError, AttributeError):
            pass
    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        request_id = request_identifier(request.headers.get("x-request-id"))
        request.state.request_id = request_id
        resource_limits = {
            ("POST", "/api/v1/images/check"): ("image", 12),
            ("GET", "/api/v1/docs/search"): ("docs", 40),
        }
        budget = resource_limits.get((request.method, request.url.path))
        denied = False
        if budget is not None:
            bucket, maximum = budget
            peer = request.client.host if request.client is not None else "<unknown>"
            denied = not request.app.state.request_limiter.allow(peer, bucket, limit=maximum)
        response: Response
        try:
            if denied:
                response = JSONResponse(
                    status_code=429,
                    content=safe_error_payload(ErrorCode.RATE_LIMITED, request_id),
                    headers={"Retry-After": "60"},
                )
            else:
                response = await call_next(request)
        except Exception:
            # No exception string, bearer, upload bytes, body, or request URL in output/logs.
            response = JSONResponse(
                status_code=500,
                content=safe_error_payload(ErrorCode.INTERNAL_ERROR, request_id),
            )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        response.headers["Cache-Control"] = "no-store"
        if request.app.state.settings.env in {"staging", "production"}:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        route = request.scope.get("route")
        pattern = getattr(route, "path", "<unmatched>")
        request.app.state.telemetry.observe(
            request.method, pattern, response.status_code, time.perf_counter() - started
        )
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "route": pattern,
                    "status": response.status_code,
                }
            )
        )
        return response
