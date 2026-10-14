"""Owner-scoped, consent-dependent feedback is untrusted until reviewed."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.persistence.models import AnalysisRecord, FeedbackRecord
from services.persistence.repository import find_account, history_consent

CHOICES = frozenset({"correct", "incorrect", "unsure", "quality_issue"})


def require_owned_completed_analysis(
    session: Session, actor: Principal, analysis_id: str
) -> tuple[str, AnalysisRecord]:
    account = find_account(session, actor)
    if account is None or not history_consent(session, account):
        raise DomainError(ErrorCode.NOT_FOUND, PUBLIC_MESSAGES[ErrorCode.NOT_FOUND], 404)
    record = session.scalar(
        select(AnalysisRecord).where(
            AnalysisRecord.id == analysis_id,
            AnalysisRecord.account_id == account.id,
            AnalysisRecord.status == "completed",
            AnalysisRecord.model_version.is_not(None),
            (AnalysisRecord.expires_at.is_(None) | (AnalysisRecord.expires_at > datetime.now(UTC))),
        )
    )
    if record is None:
        raise DomainError(ErrorCode.NOT_FOUND, PUBLIC_MESSAGES[ErrorCode.NOT_FOUND], 404)
    return account.id, record


def submit_feedback(
    session: Session, actor: Principal, analysis_id: str, choice: str
) -> FeedbackRecord:
    if choice not in CHOICES:
        raise DomainError(
            ErrorCode.INVALID_REQUEST, PUBLIC_MESSAGES[ErrorCode.INVALID_REQUEST], 422
        )
    with session.begin():
        account_id, _ = require_owned_completed_analysis(session, actor, analysis_id)
        existing = session.scalar(
            select(FeedbackRecord).where(
                FeedbackRecord.account_id == account_id,
                FeedbackRecord.analysis_id == analysis_id,
            )
        )
        if existing is not None:
            if existing.choice != choice:
                raise DomainError(ErrorCode.CONFLICT, PUBLIC_MESSAGES[ErrorCode.CONFLICT], 409)
            return existing
        record = FeedbackRecord(
            account_id=account_id,
            analysis_id=analysis_id,
            choice=choice,
            review_status="pending",
        )
        session.add(record)
        session.flush()
        return record


def get_feedback(session: Session, actor: Principal, analysis_id: str) -> FeedbackRecord:
    account_id, _ = require_owned_completed_analysis(session, actor, analysis_id)
    record = session.scalar(
        select(FeedbackRecord).where(
            FeedbackRecord.account_id == account_id,
            FeedbackRecord.analysis_id == analysis_id,
        )
    )
    if record is None:
        raise DomainError(ErrorCode.NOT_FOUND, PUBLIC_MESSAGES[ErrorCode.NOT_FOUND], 404)
    return record


def delete_feedback(session: Session, actor: Principal, analysis_id: str) -> None:
    with session.begin():
        account_id, _ = require_owned_completed_analysis(session, actor, analysis_id)
        record = session.scalar(
            select(FeedbackRecord).where(
                FeedbackRecord.account_id == account_id,
                FeedbackRecord.analysis_id == analysis_id,
            )
        )
        if record is not None:
            session.delete(record)
