"""Authenticated ephemeral image processing with consented, owner-scoped result metadata.

Never persist photographs or public-facing unvalidated disease predictions.
This route is opt-in and remains in abstention mode without genuine validated
checkpoint/calibration evidence.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.dermalens_api.dependencies import require_verified_actor
from apps.api.dermalens_api.routers.account import database_session
from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.cv.offline_pipeline import analyze_offline
from services.cv.quality import MAX_IMAGE_BYTES, InvalidImage, inspect_image
from services.persistence.models import AnalysisRecord
from services.persistence.repository import find_account, history_consent

router = APIRouter(prefix="/analyses", tags=["Protected non-diagnostic analyses"])
ALLOWED_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})
MAX_HISTORY_DAYS = 30


def _missing() -> DomainError:
    # Do not disclose whether another account owns an analysis.
    return DomainError(ErrorCode.NOT_FOUND, PUBLIC_MESSAGES[ErrorCode.NOT_FOUND], 404)


def _available(request: Request) -> None:
    if not request.app.state.settings.enable_analysis_workflow:
        raise DomainError(ErrorCode.IMAGE_CHECK_UNAVAILABLE,
                          PUBLIC_MESSAGES[ErrorCode.IMAGE_CHECK_UNAVAILABLE], 503)


def _account_with_consent(session: Session, actor: Principal) -> str:
    account = find_account(session, actor)
    if account is None or not history_consent(session, account):
        # Explicit opt-in is required before storing even non-diagnostic history.
        raise DomainError(ErrorCode.CONFLICT, PUBLIC_MESSAGES[ErrorCode.CONFLICT], 409)
    return str(account.id)


def _owned_result(session: Session, actor: Principal, analysis_id: str) -> AnalysisRecord:
    account = find_account(session, actor)
    if account is None or not history_consent(session, account):
        raise _missing()
    record = session.scalar(
        select(AnalysisRecord).where(
            AnalysisRecord.id == analysis_id,
            AnalysisRecord.account_id == account.id,
            (AnalysisRecord.expires_at.is_(None) |
             (AnalysisRecord.expires_at > datetime.now(UTC))),
        )
    )
    if record is None:
        raise _missing()
    return record


def _public(record: AnalysisRecord) -> dict[str, Any]:
    # result_json never stores bytes, class logits, or probabilities.
    stored = json.loads(record.result_json) if record.result_json else {}
    return {
        "id": record.id,
        "status": record.status,
        "model_version": record.model_version,
        "pipeline_version": record.pipeline_version,
        "created_at": record.created_at.isoformat(),
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
        "result": stored,
        "medical_diagnosis": False,
        "notice": "Research image suitability and abstention only; not a clinical diagnosis.",
    }


@router.post("", status_code=201)
async def create_analysis(
    request: Request,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, Any]:
    _available(request)
    content_type = request.headers.get("content-type", "").split(";", maxsplit=1)[0].strip().lower()
    if content_type not in ALLOWED_TYPES:
        raise DomainError(ErrorCode.INVALID_IMAGE, PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE], 415)
    length = request.headers.get("content-length", "")
    if length.isascii() and length.isdecimal() and int(length) > MAX_IMAGE_BYTES:
        raise DomainError(ErrorCode.IMAGE_TOO_LARGE,
                          PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE], 413)
    # Refuse unconsented storage before reading a personal image.
    _account_with_consent(session, actor)
    session.rollback()  # finish the read-only auth lookup before explicit write transaction
    payload = bytearray()
    async for chunk in request.stream():
        if len(payload) + len(chunk) > MAX_IMAGE_BYTES:
            raise DomainError(ErrorCode.IMAGE_TOO_LARGE,
                              PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE], 413)
        payload.extend(chunk)
    try:
        quality = inspect_image(bytes(payload))
    except InvalidImage:
        raise DomainError(ErrorCode.INVALID_IMAGE,
                          PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE], 422) from None
    except RuntimeError:
        raise DomainError(ErrorCode.IMAGE_CHECK_UNAVAILABLE,
                          PUBLIC_MESSAGES[ErrorCode.IMAGE_CHECK_UNAVAILABLE], 503) from None

    if not quality.accepted:
        result = {
            "status": "rejected",
            "reason": quality.reasons[0],
            "quality": quality.public_payload(),
            "decision": {"status": "abstained", "medical_diagnosis": False},
        }
    elif not request.app.state.model_runtime.ready:
        result = {
            "status": "abstained",
            "reason": "MODEL_NOT_READY",
            "quality": quality.public_payload(),
            "decision": {"status": "abstained", "medical_diagnosis": False,
                         "reason": "MODEL_NOT_READY"},
        }
    else:
        try:
            outcome = analyze_offline(bytes(payload), request.app.state.model_runtime)
        except (ValueError, RuntimeError):
            raise DomainError(ErrorCode.INTERNAL_ERROR,
                              PUBLIC_MESSAGES[ErrorCode.INTERNAL_ERROR], 503) from None
        result = outcome.payload()
        # Explicitly never expose/store research probabilities or claim a medical prediction.
        result["raw_research_probabilities"] = None
    del payload

    now = datetime.now(UTC)
    with session.begin():
        account_id = _account_with_consent(session, actor)
        record = AnalysisRecord(
            account_id=account_id,
            status=str(result["status"]),
            model_version=(
                str(result["model_version"]) if result.get("model_version") else None
            ),
            pipeline_version="research-offline-v1",
            created_at=now,
            expires_at=now + timedelta(days=MAX_HISTORY_DAYS),
            result_json=json.dumps(result, allow_nan=False),
        )
        session.add(record)
        session.flush()
        response = _public(record)
    return response


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: str,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, Any]:
    return _public(_owned_result(session, actor, analysis_id))


@router.delete("/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: str,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> Response:
    # Do not delete unowned records, and preserve feedback cascade.
    with session.begin():
        record = _owned_result(session, actor, analysis_id)
        session.delete(record)
    return Response(status_code=204)
