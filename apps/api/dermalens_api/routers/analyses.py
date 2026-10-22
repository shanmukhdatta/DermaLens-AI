"""Authenticated nonclinical research-only image analysis and owner results."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from apps.api.dermalens_api.dependencies import require_verified_actor
from apps.api.dermalens_api.routers.account import database_session
from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.cv.quality import MAX_IMAGE_BYTES
from services.learning.research_analysis import (
    create_research_analysis,
    delete_owned_result,
    get_owned_result,
)

router = APIRouter(prefix="/analyses", tags=["Protected experimental research"])


def _research_key(request: Request) -> str:
    config = request.app.state.settings
    if (
        not config.enable_research_analyses or config.result_encryption_key is None
        or config.env == "production"
    ):
        raise DomainError(
            ErrorCode.MODEL_NOT_READY,
            PUBLIC_MESSAGES[ErrorCode.MODEL_NOT_READY],
            503,
        )
    return config.result_encryption_key.get_secret_value()


@router.post("", status_code=201)
async def create_analysis(
    request: Request,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, object]:
    key = _research_key(request)
    if not request.app.state.model_runtime.ready:
        raise DomainError(
            ErrorCode.MODEL_NOT_READY,
            PUBLIC_MESSAGES[ErrorCode.MODEL_NOT_READY],
            503,
        )
    media = request.headers.get("content-type", "").split(";")[0].lower().strip()
    if media not in {"image/jpeg", "image/png", "image/webp"}:
        raise DomainError(
            ErrorCode.INVALID_IMAGE,
            PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE],
            415,
        )
    length = request.headers.get("content-length", "")
    if length.isascii() and length.isdecimal() and int(length) > MAX_IMAGE_BYTES:
        raise DomainError(
            ErrorCode.IMAGE_TOO_LARGE,
            PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE],
            413,
        )
    buffer = bytearray()
    async for chunk in request.stream():
        if len(buffer) + len(chunk) > MAX_IMAGE_BYTES:
            raise DomainError(
            ErrorCode.IMAGE_TOO_LARGE,
            PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE],
            413,
        )
        buffer.extend(chunk)
    return create_research_analysis(
        session, actor, bytes(buffer), request.app.state.model_runtime,
        key=key, history_days=request.app.state.settings.research_history_days,
    )


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: UUID, request: Request,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, object]:
    key = _research_key(request)
    return get_owned_result(session, actor, str(analysis_id), key=key)


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: UUID, request: Request,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> Response:
    _research_key(request)
    delete_owned_result(session, actor, str(analysis_id))
    return Response(status_code=204)
