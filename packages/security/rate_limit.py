"""Privacy-safe bounded in-memory rate limiter for expensive anonymous API routes.

Limits are per-process. Deploy behind an ingress with distributed rate limits;
never rely on this module alone to protect a multi-instance public service.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from threading import Lock


class FixedWindowLimiter:
    """Cap caller state and never retain network addresses or user identifiers."""

    def __init__(
        self,
        *,
        max_identifiers: int = 4096,
        window_seconds: int = 60,
        secret: bytes | None = None,
    ) -> None:
        if max_identifiers < 2 or window_seconds < 1:
            raise ValueError("Invalid limiter parameters")
        self.max_identifiers = max_identifiers
        self.window_seconds = window_seconds
        self._secret = secret if secret is not None else secrets.token_bytes(32)
        self._counts: dict[tuple[str, str], tuple[int, float]] = {}
        self._lock = Lock()

    def allow(
        self, ip_address: str, bucket: str, *, limit: int, now: float | None = None
    ) -> bool:
        """A full cardinality budget denies new users, never evicts active records."""
        if limit < 1 or bucket not in {"image", "docs"}:
            raise ValueError("Unrecognized resource budget")
        instant = time.monotonic() if now is None else now
        # Hash the socket peer with an instance-local random key. Never use
        # spoofable X-Forwarded-For, or store its raw value anywhere.
        opaque = hashlib.blake2b(
            ip_address.encode("utf-8"), key=self._secret, digest_size=16
        ).hexdigest()
        key = (opaque, bucket)
        with self._lock:
            existing = self._counts.get(key)
            if existing is not None and instant - existing[1] < self.window_seconds:
                count, started = existing
                if count >= limit:
                    return False
                self._counts[key] = (count + 1, started)
                return True
            # Opportunistic bounded cleanup for a new window or identity.
            if len(self._counts) >= self.max_identifiers:
                self._counts = {
                    k: value
                    for k, value in self._counts.items()
                    if instant - value[1] < self.window_seconds
                }
            if key not in self._counts and len(self._counts) >= self.max_identifiers:
                return False
            self._counts[key] = (1, instant)
            return True
