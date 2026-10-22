"""Protected owner-scoped image analysis path, persisted abstention and erasure."""
from __future__ import annotations

import io
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import inspect, select

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from packages.security.identity import Principal
from services.cv.quality import QualityReport
from services.persistence.models import AnalysisRecord, Base


class FixtureVerifiedActor:
    def verify_bearer(self, token: str) -> Principal:
        if token not in {"alice", "bob"}:
            raise ValueError("invalid fixture bearer")
        return Principal(issuer="https://issuer.fixture/", subject=token)


def _client(tmp_path: Path, *, enabled: bool = True) -> tuple[TestClient, object]:
    config = Settings(
        env="test",
        enable_analysis_workflow=enabled,
        database_url=f"sqlite+pysqlite:///{tmp_path / 'research.sqlite3'}",
        oidc_issuer="https://login.example.test/",
        oidc_audience="dermalens-integration-test",
        oidc_jwks_url="https://login.example.test/.well-known/jwks.json",
    )
    app = create_app(config)
    Base.metadata.create_all(app.state.db_engine)
    app.dependency_overrides[get_identity_verifier] = lambda: FixtureVerifiedActor()
    return TestClient(app, raise_server_exceptions=False), app


def _auth(actor: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {actor}", "Content-Type": "image/jpeg"}


def _image() -> bytes:
    fp = io.BytesIO()
    Image.new("RGB", (256, 256), color=(129, 99, 77)).save(fp, "JPEG")
    return fp.getvalue()


def _accepted(_: bytes) -> QualityReport:
    return QualityReport(
        accepted=True, reasons=(), warnings=(), width=256, height=256,
        face_count=1, blur_signal=120.0, brightness_signal=90.0,
    )


def test_requires_database_oidc_and_explicit_consent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="persistent database and signed OIDC"):
        Settings(env="test", enable_analysis_workflow=True)
    client, _ = _client(tmp_path)
    monkeypatch.setattr("apps.api.dermalens_api.routers.analyses.inspect_image", _accepted)
    with client:
        assert client.post("/api/v1/analyses", content=_image()).status_code == 401
        assert client.post("/api/v1/analyses", headers=_auth("alice"),
                           content=_image()).status_code == 409
        assert client.put("/api/v1/account/history-consent",
                          json={"enabled": True}, headers=_auth("alice")).status_code == 200


def test_owner_scoped_persistent_abstention_and_erasure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client, app = _client(tmp_path)
    monkeypatch.setattr("apps.api.dermalens_api.routers.analyses.inspect_image", _accepted)
    with client:
        for actor in ("alice", "bob"):
            assert client.put("/api/v1/account/history-consent",
                              headers=_auth(actor),
                              json={"enabled": True}).status_code == 200
        result = client.post("/api/v1/analyses", headers=_auth("alice"),
                             content=_image())
        assert result.status_code == 201, result.text
        saved = result.json()
        assert saved["medical_diagnosis"] is False
        assert saved["status"] == "abstained"
        assert saved["result"]["reason"] == "MODEL_NOT_READY"
        aid = saved["id"]
        assert client.get(f"/api/v1/analyses/{aid}", headers=_auth("alice")).status_code == 200
        assert client.get(f"/api/v1/analyses/{aid}", headers=_auth("bob")).status_code == 404
        assert client.delete(f"/api/v1/analyses/{aid}", headers=_auth("bob")).status_code == 404
        history = client.get("/api/v1/account/analyses", headers=_auth("alice")).json()
        assert len(history["items"]) == 1
        with app.state.db_session_factory() as session:
            record = session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == aid))
            assert record is not None
            assert _image().hex() not in str(record.result_json)
            assert "probabilities" not in str(record.result_json)
        assert client.delete(f"/api/v1/analyses/{aid}", headers=_auth("alice")).status_code == 204
        assert client.get(f"/api/v1/analyses/{aid}", headers=_auth("alice")).status_code == 404
        assert client.get("/api/v1/account/analyses", headers=_auth("alice")).json()["items"] == []


def test_disabled_and_body_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client, _ = _client(tmp_path, enabled=False)
    with client:
        response = client.post("/api/v1/analyses", headers=_auth("alice"), content=_image())
        assert response.status_code == 503
    client, _ = _client(tmp_path, enabled=True)
    monkeypatch.setattr("apps.api.dermalens_api.routers.analyses.inspect_image", _accepted)
    with client:
        client.put("/api/v1/account/history-consent",
                   headers=_auth("alice"), json={"enabled": True})
        assert client.post("/api/v1/analyses",
                           headers={"Authorization": "Bearer alice", "Content-Type": "text/plain"},
                           content=b"garbage").status_code == 415
        assert client.post("/api/v1/analyses",
                           headers={**_auth("alice"), "Content-Length": str(9000000)},
                           content=_image()).status_code == 413


def test_alembic_result_metadata_migration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite+pysqlite:///{tmp_path / 'schema.sqlite3'}"
    monkeypatch.setenv("DERMALENS_DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    from sqlalchemy import create_engine

    engine = create_engine(url)
    try:
        assert "result_json" in {c["name"] for c in inspect(engine).get_columns("analyses")}
    finally:
        engine.dispose()
