"""Phase 2 FastAPI composition root. No persistence, CV, RAG or feedback routes."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api.dermalens_api.config import Settings, get_settings
from apps.api.dermalens_api.middleware import RequestContextMiddleware
from apps.api.dermalens_api.readiness import ReadinessGates
from apps.api.dermalens_api.routers import models, operations
from packages.common.errors import DomainError, ErrorCode, safe_error_payload
from packages.security.identity import RejectingIdentityVerifier
from services.cv.runtime import UnavailableModelRuntime


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

    # CORS only allows a validated origin; bearer header is NOT authentication.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[config.public_web_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
        max_age=600,
    )
    # Outermost application middleware also protects unhandled errors and preflights.
    app.add_middleware(RequestContextMiddleware)
    return app


app = create_app()
