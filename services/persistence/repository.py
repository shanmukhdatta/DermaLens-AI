"""Verified-actor-scoped transactions. No caller-supplied account IDs accepted."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from packages.security.identity import Principal
from services.persistence.models import Account, AnalysisRecord, Consent

HISTORY_PURPOSE = "history_metadata"


def find_account(session: Session, actor: Principal) -> Account | None:
    return session.scalar(select(Account).where(Account.issuer == actor.issuer, Account.subject == actor.subject))


def history_consent(session: Session, account: Account | None) -> bool:
    if account is None:
        return False
    entry = session.scalar(select(Consent).where(Consent.account_id == account.id, Consent.purpose == HISTORY_PURPOSE))
    return bool(entry is not None and entry.granted)


def change_history_consent(session: Session, actor: Principal, granted: bool) -> bool:
    """Transactional opt-in; revocation immediately purges any saved analysis metadata."""
    with session.begin():
        account = find_account(session, actor)
        if account is None:
            # Do not create a persistent account for a revocation-only request.
            if not granted:
                return False
            account = Account(issuer=actor.issuer, subject=actor.subject)
            session.add(account)
            session.flush()
        entry = session.scalar(select(Consent).where(Consent.account_id == account.id, Consent.purpose == HISTORY_PURPOSE))
        if entry is None:
            entry = Consent(account_id=account.id, purpose=HISTORY_PURPOSE, granted=granted)
            session.add(entry)
        else:
            entry.granted = granted
            entry.updated_at = datetime.now(timezone.utc)
        if not granted:
            session.execute(delete(AnalysisRecord).where(AnalysisRecord.account_id == account.id))
    return granted


def owned_history(session: Session, actor: Principal) -> list[AnalysisRecord]:
    account = find_account(session, actor)
    if not history_consent(session, account) or account is None:
        return []
    now = datetime.now(timezone.utc)
    return list(session.scalars(select(AnalysisRecord).where(
        AnalysisRecord.account_id == account.id,
        (AnalysisRecord.expires_at.is_(None) | (AnalysisRecord.expires_at > now)),
    ).order_by(AnalysisRecord.created_at.desc()).limit(100)))


def erase_account(session: Session, actor: Principal) -> None:
    with session.begin():
        account = find_account(session, actor)
        if account is not None:
            session.delete(account)
