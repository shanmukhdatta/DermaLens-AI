"""FastAPI dependency injection; identity is fail-closed until Phase 3."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, Request

from apps.api.dermalens_api.readiness import ReadinessGates
from packages.common.errors import DomainError, ErrorCode, PUBLIC_MESSAGES
from packages.security.identity import IdentityVerifier, Principal


def get_readiness_gates(request: Request) -> ReadinessGates:
    return request.app.state.readiness_gates  # type: ignore[no-any-return]


def get_identity_verifier(request: Request) -> IdentityVerifier:
    return request.app.state.identity_verifier  # type: ignore[no-any-return]


def require_verified_actor(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    verifier: Annotated[IdentityVerifier, Depends(get_identity_verifier)] = None,  # type: ignore[assignment]
) -> Principal:
    """Reject anonymous/malformed claims before consulting verified provider.

    Tests may override get_identity_verifier with a deterministic test-only verifier;
    application wiring always uses RejectingIdentityVerifier in this phase.
    """
    if (
        authorization is None
        or not authorization.startswith("Bearer ")
        or not authorization[7:]
        or authorization[7:].strip() != authorization[7:]
    ):
        raise DomainError(
            ErrorCode.NOT_AUTHORIZED,
            PUBLIC_MESSAGES[ErrorCode.NOT_AUTHORIZED],
            401,
        )
    return verifier.verify_bearer(authorization[7:])
