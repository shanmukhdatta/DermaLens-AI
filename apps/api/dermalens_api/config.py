"""Typed, fail-closed configuration for Phase 1.

No secret values are logged, and no optional image storage is available yet.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Values can be configured via DERMALENS_ environment variables."""

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
        """Reject permissive wildcard origins before CORS is implemented."""
        if value == "*" or not value.startswith(("http://", "https://")):
            raise ValueError("public_web_origin must be an explicit http(s) origin")
        if "@" in value or "/" in value.split("://", maxsplit=1)[-1]:
            raise ValueError("public_web_origin must not include credentials or paths")
        return value

    @model_validator(mode="after")
    def reject_unimplemented_data_retention(self) -> Settings:
        if self.enable_image_storage or self.enable_research_image_opt_in:
            raise ValueError("image retention and research opt-in are not implemented")
        if self.env == "production" and self.public_web_origin.startswith("http://"):
            raise ValueError("production web origin must use HTTPS")
        return self


@lru_cache
def get_settings() -> Settings:
    """Production startup validates settings once; tests can inject their own."""
    return Settings()
