"""Real-model research analysis orchestrator, no clinical diagnosis claims."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.cv.artifacts import EXPECTED_CATEGORIES, preprocess_compatible
from services.cv.ports import ModelRuntime
from services.cv.quality import InvalidImage, inspect_image
from services.persistence.crypto import decrypt_result, encrypt_result
from services.persistence.models import AnalysisRecord
from services.persistence.repository import find_account, history_consent

RESEARCH_NOTICE = (
    "Experimental model output only. Not clinically validated. "
    "Do not use this result to diagnose or rule out any skin condition."
)


def _validate_prediction(model_output: object) -> dict[str, Any]:
    """Do not allow arbitrary label ordering or malformed probability values."""
    from services.cv.ports import RawPrediction

    if not isinstance(model_output, RawPrediction):
        raise ValueError("Research predictor contract not met")
    probabilities = model_output.probabilities
    labels = model_output.ordered_labels
    valid_labels = {" ".join(x.lower().replace("_", " ").split()) for x in labels}
    if (
        len(labels) != 6 or len(set(labels)) != 6
        or valid_labels != EXPECTED_CATEGORIES
        or len(probabilities) != 6
        or not all(np.isfinite(n) and 0 <= n <= 1 for n in probabilities)
        or not np.isclose(sum(probabilities), 1.0, atol=1e-3)
        or not model_output.model_id or not model_output.model_version
    ):
        raise ValueError("Invalid research model probability contract")
    selected = int(np.argmax(probabilities))
    return {
        "decision": "RESEARCH_ONLY_UNCALIBRATED",
        "research_category": labels[selected],
        "raw_model_score": round(float(probabilities[selected]), 5),
        "model": {"id": model_output.model_id, "version": model_output.model_version},
        "medical_diagnosis": False,
        "notice": RESEARCH_NOTICE,
    }


def create_research_analysis(
    session: Session, actor: Principal, image_bytes: bytes,
    runtime: ModelRuntime, *, key: str, history_days: int, detector: object | None = None
) -> dict[str, Any]:
    """Process photo in memory, persist ONLY owner-scoped encrypted small results."""
    if not runtime.ready:
        raise DomainError(
            ErrorCode.MODEL_NOT_READY,
            PUBLIC_MESSAGES[ErrorCode.MODEL_NOT_READY],
            503,
        )
    with session.begin():
        account = find_account(session, actor)
        if account is None or not history_consent(session, account):
            raise DomainError(
            ErrorCode.NOT_AUTHORIZED,
            PUBLIC_MESSAGES[ErrorCode.NOT_AUTHORIZED],
            403,
        )
        account_id = account.id
    try:
        quality = inspect_image(image_bytes, detector=detector)
    except InvalidImage as exc:
        raise DomainError(
            ErrorCode.INVALID_IMAGE,
            PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE],
            422,
        ) from exc
    if not quality.accepted:
        raise DomainError(
            ErrorCode.INVALID_IMAGE,
            PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE],
            422,
        )
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            batch = preprocess_compatible(image)
        prediction = _validate_prediction(runtime.predict(batch))
    except Exception as exc:
        raise DomainError(
            ErrorCode.INFERENCE_FAILED, PUBLIC_MESSAGES[ErrorCode.INFERENCE_FAILED], 503
        ) from exc

    now = datetime.now(UTC)
    result = {
        "status": "completed", "quality": quality.public_payload(),
        "pipeline_version": "research-full-frame-v1", **prediction,
    }
    with session.begin():
        account = find_account(session, actor)
        if account is None or account.id != account_id or not history_consent(session, account):
            raise DomainError(
            ErrorCode.NOT_AUTHORIZED,
            PUBLIC_MESSAGES[ErrorCode.NOT_AUTHORIZED],
            403,
        )
        record = AnalysisRecord(
            account_id=account_id, status="completed",
            model_version=prediction["model"]["version"],
            pipeline_version="research-full-frame-v1",
            created_at=now, expires_at=now + timedelta(days=history_days),
        )
        session.add(record)
        session.flush()
        result["analysis_id"] = record.id
        result["created_at"] = now.isoformat()
        record.result_ciphertext = encrypt_result(result, key)
    return result


def get_owned_result(
    session: Session, actor: Principal, identifier: str, *, key: str
) -> dict[str, Any]:
    account = find_account(session, actor)
    if account is None or not history_consent(session, account):
        raise DomainError(
            ErrorCode.NOT_FOUND,
            PUBLIC_MESSAGES[ErrorCode.NOT_FOUND],
            404,
        )
    record = session.scalar(
        select(AnalysisRecord).where(
            AnalysisRecord.id == identifier, AnalysisRecord.account_id == account.id,
            AnalysisRecord.expires_at > datetime.now(UTC),
            AnalysisRecord.status == "completed",
        )
    )
    if record is None or record.result_ciphertext is None:
        raise DomainError(
            ErrorCode.NOT_FOUND,
            PUBLIC_MESSAGES[ErrorCode.NOT_FOUND],
            404,
        )
    try:
        return decrypt_result(record.result_ciphertext, key)
    except ValueError as exc:
        raise DomainError(
            ErrorCode.INTERNAL_ERROR, PUBLIC_MESSAGES[ErrorCode.INTERNAL_ERROR], 503
        ) from exc


def delete_owned_result(session: Session, actor: Principal, identifier: str) -> None:
    with session.begin():
        account = find_account(session, actor)
        if account is None or not history_consent(session, account):
            raise DomainError(
            ErrorCode.NOT_FOUND,
            PUBLIC_MESSAGES[ErrorCode.NOT_FOUND],
            404,
        )
        record = session.scalar(select(AnalysisRecord).where(
            AnalysisRecord.id == identifier, AnalysisRecord.account_id == account.id,
        ))
        if record is None:
            raise DomainError(
            ErrorCode.NOT_FOUND,
            PUBLIC_MESSAGES[ErrorCode.NOT_FOUND],
            404,
        )
        session.delete(record)
