"""Bounded retention sweeps for expiring stored analysis metadata.

This is an offline operator function, never a public HTTP endpoint. It never
loads raw photographs and has no dependency on a medical inference model.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from services.persistence.models import AnalysisRecord

MAX_SWEEP_SIZE = 5000


def prune_expired_analyses(
    session: Session,
    *,
    cutoff: datetime | None = None,
    max_records: int = 250,
    dry_run: bool = True,
) -> int:
    """Count or delete a single ordered, transaction-bounded batch of expired records.

    Associated feedback is removed by the database's ON DELETE CASCADE FK.
    Returns the count of matching rows (dry run) or rows actually deleted.
    Does not touch records with a NULL or future expiration.
    """
    if not 1 <= max_records <= MAX_SWEEP_SIZE:
        raise ValueError("max_records must be between 1 and MAX_SWEEP_SIZE")
    boundary = cutoff if cutoff is not None else datetime.now(UTC)
    if boundary.tzinfo is None or boundary.utcoffset() is None:
        raise ValueError("cutoff must be timezone-aware")
    with session.begin():
        target_ids = list(
            session.scalars(
                select(AnalysisRecord.id)
                .where(
                    AnalysisRecord.expires_at.is_not(None),
                    AnalysisRecord.expires_at <= boundary,
                )
                .order_by(AnalysisRecord.expires_at, AnalysisRecord.id)
                .limit(max_records)
            )
        )
        if dry_run or not target_ids:
            return len(target_ids)
        deleted = session.execute(
            delete(AnalysisRecord).where(
                AnalysisRecord.id.in_(target_ids),
                AnalysisRecord.expires_at <= boundary,
            )
        )
        if not isinstance(deleted, CursorResult):
            raise RuntimeError("Expected cursor result for deletion")
        return max(0, deleted.rowcount)
