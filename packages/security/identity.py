"""Identity and ownership ports; no tokens are trusted in Phase 2."""

from __future__ import annotations

from dataclasses import dataclass
from hmac import compare_digest
from typing import Protocol

from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode


@dataclass(frozen=True, slots=True)
class Principal:
    """A subject produced by a future signature- and issuer-verifying OIDC adapter."""

    subject: str
    issuer: str


class IdentityVerifier(Protocol):
    """Only a cryptographically verified provider may construct an authenticated principal."""

    def verify_bearer(self, token: str) -> Principal: ...


class RejectingIdentityVerifier:
    """Default production wiring: even well-formed bearer tokens are NOT authenticated."""

    def verify_bearer(self, token: str) -> Principal:
        del token
        raise DomainError(
            ErrorCode.NOT_AUTHORIZED,
            PUBLIC_MESSAGES[ErrorCode.NOT_AUTHORIZED],
            401,
        )


def ensure_owner(principal: Principal, owner_subject: str) -> None:
    """Suppress cross-owner existence information; no self-asserted actor IDs."""
    if not owner_subject or not compare_digest(principal.subject, owner_subject):
        raise DomainError(ErrorCode.NOT_FOUND, PUBLIC_MESSAGES[ErrorCode.NOT_FOUND], 404)
