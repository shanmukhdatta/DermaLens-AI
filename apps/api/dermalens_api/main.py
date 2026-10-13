"""Phase 1 HTTP entrypoint: health and readiness only.

Do not add analysis, storage, auth or chatbot routes until their respective phases.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.api.dermalens_api.config import Settings, get_settings
from packages.common.errors import DomainError
from services.cv.runtime import UnavailableModelRuntime


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an independently testable app without initializing private services."""
    config = settings or get_settings()
    app = FastAPI(
        title="DermaLens AI — Engineering Foundation",
        version="0.1.0",
        description="Research prototype; model inference is not available.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.settings = config
    app.state.model_runtime = UnavailableModelRuntime()

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, error: DomainError) -> JSONResponse:
        del request
        return JSONResponse(status_code=error.status_code, content=error.as_payload())

    @app.get("/api/v1/health", tags=["Operations"])
    def liveness() -> dict[str, str]:
        """Process liveness; never claim model readiness."""
        return {"status": "ok"}

    @app.get("/api/v1/readiness", tags=["Operations"])
    def readiness() -> JSONResponse:
        """Fail closed until real model, policy and downstream gates exist."""
        return JSONResponse(status_code=503, content={"status": "not_ready"})

    return app


app = create_app()
