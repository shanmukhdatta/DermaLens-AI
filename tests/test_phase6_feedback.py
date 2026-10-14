"""Phase 6 feedback tests: owned history, verified actors and moderation."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from packages.security.identity import Principal
from services.persistence.models import Account, AnalysisRecord, Base, FeedbackRecord


class TestOnlyIdentity:
    def verify_bearer(self, token: str) -> Principal:
        assert token in {"alice", "bob"}
        return Principal(subject=token, issuer="https://test-issuer.example/")


def auth(who: str) -> dict[str, str]:
    return {"Authorization": "Bearer " + who}


def test_feedback_requires_verified_ownership_and_real_analysis(tmp_path: Path) -> None:
    app = create_app(Settings(env="test", database_url=f"sqlite+pysqlite:///{tmp_path / 'feedback.db'}"))
    Base.metadata.create_all(app.state.db_engine)
    app.dependency_overrides[get_identity_verifier] = lambda: TestOnlyIdentity()
    with TestClient(app, raise_server_exceptions=False) as client:
        for who in ("alice", "bob"):
            res = client.put(
                "/api/v1/account/history-consent", json={"enabled": True}, headers=auth(who)
            )
            assert res.status_code == 200
        with app.state.db_session_factory.begin() as db:
            owner = db.scalar(select(Account).where(Account.subject == "alice"))
            assert owner is not None
            fixture = AnalysisRecord(
                account_id=owner.id,
                status="completed",
                model_version="test-fixture-only",
                pipeline_version="test",
            )
            db.add(fixture)
            db.flush()
            analysis_id = fixture.id
        endpoint = f"/api/v1/analyses/{analysis_id}/feedback"
        assert client.post(endpoint, json={"choice": "correct"}).status_code == 401
        assert client.post(endpoint, headers=auth("bob"), json={"choice": "incorrect"}).status_code == 404
        assert client.get(endpoint, headers=auth("bob")).status_code == 404
        assert client.post(endpoint, headers=auth("alice"), json={"choice": "medical_advice"}).status_code == 422
        result = client.post(endpoint, headers=auth("alice"), json={"choice": "unsure"})
        assert result.status_code == 201
        assert result.json()["review_status"] == "pending"
        assert client.post(endpoint, headers=auth("alice"), json={"choice": "unsure"}).json() == result.json()
        assert client.post(endpoint, headers=auth("alice"), json={"choice": "incorrect"}).status_code == 409
        assert client.get(endpoint, headers=auth("alice")).json() == result.json()
        assert client.delete(endpoint, headers=auth("bob")).status_code == 404
        assert client.delete(endpoint, headers=auth("alice")).status_code == 204
        assert client.get(endpoint, headers=auth("alice")).status_code == 404
        client.post(endpoint, headers=auth("alice"), json={"choice": "quality_issue"})
        exported = client.get("/api/v1/account/export", headers=auth("alice"))
        assert exported.status_code == 200
        assert exported.json()["feedback"][0]["choice"] == "quality_issue"
        client.put("/api/v1/account/history-consent", headers=auth("alice"), json={"enabled": False})
        assert client.get(endpoint, headers=auth("alice")).status_code == 404
    with app.state.db_session_factory() as db:
        assert list(db.scalars(select(FeedbackRecord))) == []
