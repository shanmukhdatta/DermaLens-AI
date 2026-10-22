"""Typed runtime settings; reject permissive and unsafe configurations at startup."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Only explicitly exposed DERMALENS_ keys control the API."""

    model_config = SettingsConfigDict(
        env_prefix="DERMALENS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: Literal["development", "test", "staging", "production"] = "development"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    public_web_origin: str = "http://localhost:3000"
    enable_image_storage: bool = False
    enable_research_image_opt_in: bool = False
    enable_image_quality_checks: bool = False
    enable_rag_assistant: bool = False
    # Gated, non-clinical research-only analysis workflow.
    enable_research_analyses: bool = False
    result_encryption_key: SecretStr | None = None
    model_manifest_path: str | None = None
    model_checkpoint_path: str | None = None
    model_label_map_path: str | None = None
    research_history_days: int = Field(default=30, ge=1, le=90)
    grok_api_key: SecretStr | None = None
    grok_model: str = "grok-4.7"
    database_url: str | None = None
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None

    @field_validator("public_web_origin")
    @classmethod
    def validate_origin(cls, value: str) -> str:
        """Require one canonical origin; never accept credentials, wildcard or path."""
        if not value or value != value.strip() or any(c.isspace() for c in value):
            raise ValueError("public_web_origin must be a canonical origin")
        try:
            url = urlsplit(value)
            port = url.port  # Force numeric port validation.
        except ValueError as exc:
            raise ValueError("public_web_origin has an invalid URL or port") from exc
        if (
            url.scheme not in {"http", "https"}
            or not url.hostname
            or url.username is not None
            or url.password is not None
            or url.path
            or url.query
            or url.fragment
            or "*" in url.netloc
            or not url.netloc
        ):
            raise ValueError("public_web_origin must be an explicit http(s) origin")
        if port is not None and not 1 <= port <= 65535:
            raise ValueError("public_web_origin has an invalid port")
        if url.geturl() != value:
            raise ValueError("public_web_origin must be canonical")
        return value

    @model_validator(mode="after")
    def reject_unimplemented_data_retention(self) -> Settings:
        if self.enable_image_storage or self.enable_research_image_opt_in:
            raise ValueError("image retention and research opt-in are not implemented")
        if self.enable_rag_assistant and (
            self.grok_api_key is None or not self.grok_api_key.get_secret_value()
        ):
            raise ValueError("RAG requires a server-side Grok API key")
        if self.enable_research_analyses:
            if self.env == "production":
                raise ValueError("unvalidated research analysis must not run in production")
            if not self.database_url or not self.result_encryption_key:
                raise ValueError("research analysis requires persistence and result encryption")
            if self.env != "test" and not all(
                (self.model_manifest_path, self.model_checkpoint_path, self.model_label_map_path)
            ):
                raise ValueError("a real verified research model package is required")
            from cryptography.fernet import Fernet

            try:
                Fernet(self.result_encryption_key.get_secret_value().encode("ascii"))
            except (ValueError, TypeError, UnicodeError) as exc:
                raise ValueError("invalid research result encryption key") from exc
        credentials = (self.oidc_issuer, self.oidc_audience, self.oidc_jwks_url)
        if any(value is not None for value in credentials) and not all(credentials):
            raise ValueError("OIDC issuer, audience and JWKS URL must be set together")
        if self.database_url is not None:
            if not self.database_url.startswith(("postgresql+psycopg://", "sqlite+pysqlite://")):
                raise ValueError("database_url must use PostgreSQL or test SQLite")
            if self.env in {"staging", "production"} and not self.database_url.startswith(
                "postgresql+psycopg://"
            ):
                raise ValueError("staging/production persistence requires PostgreSQL")
        url = urlsplit(self.public_web_origin)
        if self.env in {"staging", "production"} and url.scheme != "https":
            raise ValueError("non-development web origin must use HTTPS")
        if url.scheme == "http" and url.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("plaintext web origin is allowed only for local development")
        return self


@lru_cache
def get_settings() -> Settings:
    """Validated process configuration; tests use create_app(Settings(...))."""
    return Settings()
