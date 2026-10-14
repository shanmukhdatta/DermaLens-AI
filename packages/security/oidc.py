"""OIDC JWT verifier: cryptographic signature and claims validation, no trust in JWT payload alone."""

from __future__ import annotations

from urllib.parse import urlsplit

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal


class OidcJwtVerifier:
    def __init__(
        self, issuer: str, audience: str, jwks_url: str, *, client: PyJWKClient | None = None
    ) -> None:
        issuer_parts = urlsplit(issuer)
        key_parts = urlsplit(jwks_url)
        if (
            issuer_parts.scheme != "https"
            or key_parts.scheme != "https"
            or not issuer_parts.hostname
            or issuer_parts.hostname != key_parts.hostname
            or not audience
            or issuer_parts.username
            or key_parts.username
            or issuer_parts.password
            or key_parts.password
            or key_parts.fragment
        ):
            raise ValueError("OIDC issuer and JWKS must be valid HTTPS URLs on the same host")
        self.issuer = issuer
        self.audience = audience
        self.client = (
            client if client is not None else PyJWKClient(jwks_url, lifespan=300, timeout=5)
        )

    def verify_bearer(self, token: str) -> Principal:
        try:
            header = jwt.get_unverified_header(token)
            if header.get("alg") != "RS256" or not isinstance(header.get("kid"), str):
                raise ValueError("Unsupported JWT signing algorithm")
            signing_key = self.client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iat", "iss", "aud", "sub"]},
                leeway=30,
            )
            subject = claims["sub"]
            if not isinstance(subject, str) or not subject or len(subject) > 255:
                raise ValueError("Invalid OIDC subject")
            return Principal(subject=subject, issuer=self.issuer)
        except (PyJWTError, ValueError, TypeError, KeyError, OSError) as exc:
            raise DomainError(
                ErrorCode.NOT_AUTHORIZED, PUBLIC_MESSAGES[ErrorCode.NOT_AUTHORIZED], 401
            ) from exc
