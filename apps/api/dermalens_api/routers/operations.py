"""Public operational endpoints. These never prove clinical/model readiness."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from apps.api.dermalens_api.dependencies import get_readiness_gates
from apps.api.dermalens_api.readiness import ReadinessGates

router = APIRouter(tags=["Operations"])


@router.get("/health")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness", response_model=None)
def readiness(gates: Annotated[ReadinessGates, Depends(get_readiness_gates)]) -> JSONResponse:
    if not gates.ready():
        return JSONResponse(status_code=503, content={"status": "not_ready"})
    return JSONResponse(status_code=200, content={"status": "ok"})
