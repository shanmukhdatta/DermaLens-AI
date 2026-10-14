"""Request correlation, privacy-minimal access records, and uniform security headers."""

from __future__ import annotations

import json
import logging
from time import perf_counter
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from packages.common.errors import ErrorCode, safe_error_payload
from packages.telemetry.metrics import RouteMetrics

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
        started_at = perf_counter()
        request_id = request_identifier(request.headers.get("x-request-id"))
        request.state.request_id = request_id
        try:
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
        duration_ms = round((perf_counter() - started_at) * 1000.0, 3)
        metrics = getattr(request.app.state, "route_metrics", None)
        if isinstance(metrics, RouteMetrics):
            metrics.observe(request.method, pattern, response.status_code, duration_ms)
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "route": pattern,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                }
            )
        )
        return response
