"""Typed runtime settings; reject permissive and unsafe configurations at startup."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
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
