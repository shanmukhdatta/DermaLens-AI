"""Fail-closed research API composition root; opt-in feature boundaries."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from apps.api.dermalens_api.config import Settings, get_settings
from apps.api.dermalens_api.middleware import RequestContextMiddleware
from apps.api.dermalens_api.readiness import ReadinessGates
from apps.api.dermalens_api.routers import account, docs_search, feedback, images, models, operations
from packages.common.errors import DomainError, ErrorCode, safe_error_payload
from packages.security.identity import RejectingIdentityVerifier
from packages.security.oidc import OidcJwtVerifier
from packages.telemetry.runtime import RuntimeTelemetry
from services.cv.runtime import UnavailableModelRuntime
from services.persistence.runtime import build_database


def _request_id(request: Request) -> str:
    return request.state.request_id  # type: ignore[no-any-return]


def create_app(settings: Settings | None = None) -> FastAPI:
    """Wire only real capabilities; DI overrides are isolated per app for unit tests."""
    config = settings if settings is not None else get_settings()
    app = FastAPI(
        title="DermaLens AI — Research API",
        version="0.2.0",
        description="Engineering-only research prototype; no diagnosis or image inference.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        debug=False,
    )
    app.state.settings = config
    app.state.model_runtime = UnavailableModelRuntime()
    app.state.readiness_gates = ReadinessGates(model_runtime=app.state.model_runtime)
    app.state.identity_verifier = RejectingIdentityVerifier()
    app.state.db_session_factory = None
    if config.oidc_issuer and config.oidc_audience and config.oidc_jwks_url:
        app.state.identity_verifier = OidcJwtVerifier(
            config.oidc_issuer, config.oidc_audience, config.oidc_jwks_url
        )
    if config.database_url:
        app.state.db_engine, app.state.db_session_factory = build_database(config.database_url)
    if config.enable_rag_assistant:
        from services.rag.grok import GrokResponseProvider
        from services.rag.index import DocumentationIndex

        assert config.grok_api_key is not None
        app.state.docs_index = DocumentationIndex.from_repository(
            Path(__file__).resolve().parents[3]
        )
        app.state.docs_provider = GrokResponseProvider(
            config.grok_api_key.get_secret_value(), config.grok_model
        )

    @app.exception_handler(DomainError)
    async def on_domain_error(request: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content=safe_error_payload(error.code, _request_id(request)),
        )

    @app.exception_handler(RequestValidationError)
    async def on_validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        del error
        return JSONResponse(
            status_code=422,
            content=safe_error_payload(ErrorCode.INVALID_REQUEST, _request_id(request)),
        )

    @app.exception_handler(HTTPException)
    async def on_http_error(request: Request, error: HTTPException) -> JSONResponse:
        code = ErrorCode.NOT_FOUND
        if error.status_code == 405:
            code = ErrorCode.METHOD_NOT_ALLOWED
        elif error.status_code in {401, 403}:
            code = ErrorCode.NOT_AUTHORIZED
        elif error.status_code == 422:
            code = ErrorCode.INVALID_REQUEST
        elif error.status_code >= 500:
            code = ErrorCode.INTERNAL_ERROR
        return JSONResponse(
            status_code=error.status_code,
            content=safe_error_payload(code, _request_id(request)),
        )

    app.include_router(operations.router, prefix="/api/v1")
    app.include_router(models.router, prefix="/api/v1")
    app.include_router(account.router, prefix="/api/v1")
    app.include_router(images.router, prefix="/api/v1")
    app.include_router(docs_search.router, prefix="/api/v1")
    app.include_router(feedback.router, prefix="/api/v1")
    if config.enable_rag_assistant:
        from apps.api.dermalens_api.routers import copilot

        app.include_router(copilot.router, prefix="/api/v1")

    # Metric label allowlist is fixed at app construction, never derived from request paths.
    app.state.telemetry = RuntimeTelemetry(
        frozenset(route.path for route in app.routes if hasattr(route, "path"))
    )

    # CORS only allows a validated origin; bearer header is NOT authentication.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.public_web_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
        max_age=600,
    )
    # Outermost application middleware also protects unhandled errors and preflights.
    app.add_middleware(RequestContextMiddleware)
    return app


app = create_app()
