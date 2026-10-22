"""Test that expiry removes only eligible metadata and dependent feedback."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import select

from services.persistence.models import Account, AnalysisRecord, Base, FeedbackRecord
from services.persistence.retention import prune_expired_analyses
from services.persistence.runtime import build_database


def test_sweep_is_dry_by_default_and_cascades_only_expired(tmp_path: Path) -> None:
    engine, factory = build_database(f"sqlite+pysqlite:///{tmp_path / 'retention.db'}")
    Base.metadata.create_all(engine)
    now = datetime.now(UTC)
    try:
        with factory.begin() as session:
            account = Account(issuer="https://example.test", subject="fixture")
            session.add(account)
            session.flush()
            expired = AnalysisRecord(
                account_id=account.id, status="completed", model_version="fixture",
                expires_at=now - timedelta(days=1),
            )
            future = AnalysisRecord(
                account_id=account.id, status="completed",
                expires_at=now + timedelta(days=1),
            )
            permanent = AnalysisRecord(account_id=account.id, status="completed")
            session.add_all([expired, future, permanent])
            session.flush()
            ids = (expired.id, future.id, permanent.id)
            session.add(
                FeedbackRecord(
                    account_id=account.id, analysis_id=expired.id, choice="unsure",
                )
            )
        with factory() as session:
            assert prune_expired_analyses(session, cutoff=now) == 1
        with factory() as session:
            assert set(session.scalars(select(AnalysisRecord.id))) == set(ids)
            assert len(list(session.scalars(select(FeedbackRecord.id)))) == 1
        with factory() as session:
            assert prune_expired_analyses(session, cutoff=now, dry_run=False) == 1
        with factory() as session:
            assert prune_expired_analyses(session, cutoff=now, dry_run=False) == 0
        with factory() as session:
            assert set(session.scalars(select(AnalysisRecord.id))) == set(ids[1:])
            assert list(session.scalars(select(FeedbackRecord.id))) == []
    finally:
        engine.dispose()


def test_sweep_is_bounded_and_rejects_unsafe_cutoff(tmp_path: Path) -> None:
    engine, factory = build_database(f"sqlite+pysqlite:///{tmp_path / 'bounded.db'}")
    Base.metadata.create_all(engine)
    now = datetime.now(UTC)
    try:
        with factory.begin() as session:
            account = Account(issuer="https://example.test", subject="fixture")
            session.add(account)
            session.flush()
            session.add_all(
                AnalysisRecord(
                    account_id=account.id, status="completed",
                    expires_at=now - timedelta(hours=1),
                )
                for _ in range(3)
            )
        for expected in (2, 1, 0):
            with factory() as session:
                assert (
                    prune_expired_analyses(
                        session, cutoff=now, max_records=2, dry_run=False
                    )
                    == expected
                )
        with factory() as session:
            with pytest.raises(ValueError, match="max_records"):
                prune_expired_analyses(session, max_records=0)
            with pytest.raises(ValueError, match="timezone-aware"):
                prune_expired_analyses(session, cutoff=datetime(2026, 1, 1))
    finally:
        engine.dispose()
