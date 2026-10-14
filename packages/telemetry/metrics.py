"""Privacy-minimal local request instrumentation; no user or image-level labels."""
from __future__ import annotations

from collections import defaultdict
from threading import Lock


class RouteMetrics:
    """Per-process counters; no public metrics endpoint and no high-cardinality labels."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counts: dict[tuple[str, str, int], int] = defaultdict(int)
        self._total_ms: dict[tuple[str, str, int], float] = defaultdict(float)

    def observe(self, method: str, pattern: str, status: int, duration_ms: float) -> None:
        # Route patterns are predefined; never use a full URL, token, subject or photo metadata.
        route = pattern if pattern.startswith("/api/v1/") else "<unmatched>"
        if not method.isalpha() or duration_ms < 0:
            return
        key = (method.upper(), route, status)
        with self._lock:
            self._counts[key] += 1
            self._total_ms[key] += duration_ms

    def snapshot(self) -> list[dict[str, str | float | int]]:
        """For internal tests/operators; intentionally not served over the public API."""
        with self._lock:
            return [
                {
                    "method": method,
                    "route": route,
                    "status": status,
                    "requests": amount,
                    "mean_duration_ms": round(self._total_ms[key] / amount, 3),
                }
                for key, amount in sorted(self._counts.items())
                for method, route, status in [key]
            ]
