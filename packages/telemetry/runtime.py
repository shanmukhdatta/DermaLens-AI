"""Bounded, privacy-preserving in-process operational telemetry.

This is a lightweight developer/staging baseline, not a durable metrics store.
No headers, paths with user input, upload bytes, identity or image content are saved.
"""
from __future__ import annotations

from collections import Counter
from threading import Lock
from typing import Any

# Inclusive latency thresholds, in milliseconds.
LATENCY_BUCKETS = (50, 100, 250, 500, 1000, 2000, 5000)


class RuntimeTelemetry:
    """Thread-safe aggregate counts over a fixed, known list of route templates."""

    def __init__(self, allowed_routes: frozenset[str] | None = None) -> None:
        self._allowed_routes = allowed_routes if allowed_routes is not None else frozenset()
        self._request_groups: Counter[tuple[str, str, str]] = Counter()
        self._latency_buckets: Counter[str] = Counter()
        self._total = 0
        self._lock = Lock()

    def observe(
        self, method: str, route_template: str | None, status: int, duration_seconds: float
    ) -> None:
        """Never accept a raw URL/path as a label; only registered route templates."""
        route = route_template if route_template in self._allowed_routes else "<unmatched>"
        safe_methods = {"GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS"}
        safe_method = method if method in safe_methods else "OTHER"
        group = f"{status // 100}xx" if 100 <= status < 600 else "other"
        ms = max(0.0, duration_seconds) * 1000.0
        bucket = next((str(limit) for limit in LATENCY_BUCKETS if ms <= limit), "+Inf")
        with self._lock:
            self._request_groups[(route, safe_method, group)] += 1
            self._latency_buckets[bucket] += 1
            self._total += 1

    def snapshot(self) -> dict[str, Any]:
        """Aggregates are intended for internal operators, never a public endpoint."""
        with self._lock:
            routes = [
                {"route": route, "method": method, "status_family": family, "requests": count}
                for (route, method, family), count in sorted(self._request_groups.items())
            ]
            buckets = {
                name: self._latency_buckets[name]
                for name in (*[str(v) for v in LATENCY_BUCKETS], "+Inf")
            }
            return {"total_requests": self._total, "routes": routes, "latency_buckets_ms": buckets}
