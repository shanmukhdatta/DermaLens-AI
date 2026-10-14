"""Phase 3 account, consent, ownership, crypto and migration regression tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import jwt
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import select

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from packages.common.errors import DomainError
from packages.security.identity import Principal
from packages.security.oidc import OidcJwtVerifier
from services.persistence.models import Account, AnalysisRecord, Base


class VerifiedTestActor:
    """Tests only; never registered in normal application startup."""

    def verify_bearer(self, token: str) -> Principal:
        if token not in {"alice", "bob"}:
            raise ValueError("Only fixture tokens allowed")
        return Principal(subject=token, issuer="https://fixture-issuer.test/")


def make_client(tmp_path: Path) -> tuple[TestClient, object]:
    url = f"sqlite+pysqlite:///{tmp_path / 'test.sqlite'}"
    app = create_app(Settings(env="test", database_url=url))
    Base.metadata.create_all(app.state.db_engine)
    app.dependency_overrides[get_identity_verifier] = lambda: VerifiedTestActor()
    return TestClient(app, raise_server_exceptions=False), app


def auth(subject: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {subject}"}


def test_requires_real_identity_and_configured_database(tmp_path: Path) -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        assert client.get("/api/v1/account").status_code == 401
    app.dependency_overrides[get_identity_verifier] = lambda: VerifiedTestActor()
    with TestClient(app) as client:
        response = client.get("/api/v1/account", headers=auth("alice"))
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


def test_history_consent_is_owned_and_idempotent(tmp_path: Path) -> None:
    client, app = make_client(tmp_path)
    with client:
        assert client.get("/api/v1/account", headers=auth("alice")).json() == {"history_enabled": False}
        for _ in range(2):
            response = client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": True})
            assert response.status_code == 200
            assert response.json() == {"history_enabled": True}
        assert client.get("/api/v1/account", headers=auth("bob")).json() == {"history_enabled": False}
        assert client.get("/api/v1/account/analyses", headers=auth("bob")).json() == {"items": []}
        assert client.get("/api/v1/account/export", headers=auth("alice")).json() == {"history_enabled": True, "analyses": []}
        assert client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": "yes"}).status_code == 422
        assert client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": True, "owner_id": "bob"}).status_code == 422
    with app.state.db_session_factory() as session:
        assert len(list(session.scalars(select(Account)))) == 1


def test_revocation_purges_history_and_account_deletes(tmp_path: Path) -> None:
    client, app = make_client(tmp_path)
    with client:
        client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": True})
        client.put("/api/v1/account/history-consent", headers=auth("bob"), json={"enabled": True})
        with app.state.db_session_factory.begin() as session:
            accounts = {account.subject: account for account in session.scalars(select(Account))}
            session.add(AnalysisRecord(account_id=accounts["alice"].id, status="ready"))
            session.add(AnalysisRecord(account_id=accounts["bob"].id, status="ready"))
        assert len(client.get("/api/v1/account/analyses", headers=auth("alice")).json()["items"]) == 1
        assert len(client.get("/api/v1/account/analyses", headers=auth("bob")).json()["items"]) == 1
        assert client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": False}).json() == {"history_enabled": False}
        assert client.get("/api/v1/account/analyses", headers=auth("alice")).json() == {"items": []}
        assert len(client.get("/api/v1/account/analyses", headers=auth("bob")).json()["items"]) == 1
        assert client.delete("/api/v1/account", headers=auth("bob")).status_code == 204
        assert client.delete("/api/v1/account", headers=auth("bob")).status_code == 204
    with app.state.db_session_factory() as session:
        assert list(session.scalars(select(AnalysisRecord))) == []


def test_migration_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite+pysqlite:///{tmp_path / 'migration.sqlite'}"
    monkeypatch.setenv("DERMALENS_DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    from sqlalchemy import inspect, create_engine
    engine = create_engine(url)
    assert {"accounts", "consents", "analyses", "feedback"}.issubset(set(inspect(engine).get_table_names()))
    engine.dispose()
    command.downgrade(config, "base")
    engine = create_engine(url)
    assert "accounts" not in inspect(engine).get_table_names()
    engine.dispose()


def test_oidc_enforces_signature_and_claims() -> None:
    issuer = "https://id.example.com/"
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    class StaticJwks:
        def get_signing_key_from_jwt(self, token: str) -> SimpleNamespace:
            del token
            return SimpleNamespace(key=private_key.public_key())
    verifier = OidcJwtVerifier(issuer, "dermalens-api", issuer + "keys", client=StaticJwks())  # type: ignore[arg-type]
    now = datetime.now(timezone.utc)
    claims = {"sub": "alice", "iss": issuer, "aud": "dermalens-api",
              "iat": now, "exp": now + timedelta(minutes=5)}
    token = jwt.encode(claims, private_key, algorithm="RS256", headers={"kid": "fixture"})
    assert verifier.verify_bearer(token) == Principal(subject="alice", issuer=issuer)
    for invalid in (
        jwt.encode({**claims, "aud": "attacker"}, private_key, algorithm="RS256", headers={"kid": "fixture"}),
        jwt.encode({**claims, "exp": now - timedelta(minutes=5)}, private_key, algorithm="RS256", headers={"kid": "fixture"}),
        jwt.encode({**claims, "sub": ""}, private_key, algorithm="RS256", headers={"kid": "fixture"}),
        jwt.encode(claims, "not-a-key", algorithm="HS256", headers={"kid": "fixture"}),
    ):
        with pytest.raises(DomainError) as exc:
            verifier.verify_bearer(invalid)
        assert exc.value.status_code == 401
