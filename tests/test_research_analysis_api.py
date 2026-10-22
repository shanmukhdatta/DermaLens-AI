"""End-to-end API behavior with isolated deterministic fixture model.

The fixture is deliberately not shipped as application inference and provides
no accuracy or clinical validation evidence.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import SecretStr
from sqlalchemy import select

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from packages.security.identity import Principal
from services.cv.ports import RawPrediction
from services.persistence.crypto import decrypt_result, encrypt_result
from services.persistence.models import AnalysisRecord, Base


class VerifiedFixtureActor:
    def verify_bearer(self, token: str) -> Principal:
        assert token in {"alice", "bob"}
        return Principal(subject=token, issuer="https://fixture-issuer.test/")


class OneFaceFixture:
    def detect(self, image: np.ndarray) -> list[tuple[int, int, int, int]]:
        return [(50, 50, 200, 200)]


class FixtureModel:
    """Test-only interface; never registered in production app creation."""

    @property
    def ready(self) -> bool:
        return True

    def predict(self, batch: np.ndarray) -> RawPrediction:
        assert batch.shape == (1, 224, 224, 3)
        return RawPrediction(
            model_id="fixture-unit-test", model_version="fixture-v1",
            ordered_labels=(
                "Acne", "Fungal Infection", "Hyperpigmentation",
                "Normal Skin", "Skin Cancer", "Vitiligo",
            ),
            probabilities=(0.3, 0.1, 0.2, 0.15, 0.1, 0.15),
        )


def photo() -> bytes:
    output = BytesIO()
    Image.new("RGB", (400, 400), (142, 121, 106)).save(output, format="JPEG")
    return output.getvalue()


def headers(user: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user}", "Content-Type": "image/jpeg"}


def test_gated_research_upload_and_private_encrypted_history(
    tmp_path: Path, monkeypatch: object
) -> None:
    import pytest
    assert isinstance(monkeypatch, pytest.MonkeyPatch)
    monkeypatch.setattr("services.cv.quality.HaarFaceDetector", OneFaceFixture)
    key = Fernet.generate_key().decode()
    app = create_app(Settings(
        env="test", database_url=f"sqlite+pysqlite:///{tmp_path / 'db.sqlite3'}",
        enable_research_analyses=True, result_encryption_key=SecretStr(key),
    ))
    Base.metadata.create_all(app.state.db_engine)
    app.state.model_runtime = FixtureModel()
    app.dependency_overrides[get_identity_verifier] = lambda: VerifiedFixtureActor()
    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.post("/api/v1/analyses", content=photo()).status_code == 401
        # Consent is an opt-in prerequisite for any persisted model output.
        assert (
            client.post("/api/v1/analyses", content=photo(), headers=headers("alice")).status_code
            == 403
        )
        assert client.put(
            "/api/v1/account/history-consent",
            json={"enabled": True},
            headers={"Authorization": "Bearer alice"},
        ).status_code == 200
        response = client.post("/api/v1/analyses", content=photo(), headers=headers("alice"))
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["decision"] == "RESEARCH_ONLY_UNCALIBRATED"
        assert body["medical_diagnosis"] is False
        assert body["research_category"] == "Acne"
        assert body["model"]["version"] == "fixture-v1"
        identifier = body["analysis_id"]
        assert client.get(f"/api/v1/analyses/{identifier}").status_code == 401
        assert client.get(
            f"/api/v1/analyses/{identifier}", headers=headers("bob")
        ).status_code == 404
        assert client.get(
            f"/api/v1/analyses/{identifier}", headers=headers("alice")
        ).json() == body
        with app.state.db_session_factory() as session:
            saved = session.scalar(select(AnalysisRecord).where(AnalysisRecord.id == identifier))
            assert saved is not None and saved.result_ciphertext is not None
            assert b"Acne" not in saved.result_ciphertext
            assert decrypt_result(saved.result_ciphertext, key)["analysis_id"] == identifier
        assert client.delete(
            f"/api/v1/analyses/{identifier}", headers=headers("bob")
        ).status_code == 404
        assert client.delete(
            f"/api/v1/analyses/{identifier}", headers=headers("alice")
        ).status_code == 204
        assert client.get(
            f"/api/v1/analyses/{identifier}", headers=headers("alice")
        ).status_code == 404


def test_fails_closed_without_research_configuration() -> None:
    client = TestClient(create_app(Settings(env="test")), raise_server_exceptions=False)
    with client:
        assert client.post("/api/v1/analyses").status_code == 404


def test_authenticated_encryption_rejects_tampering() -> None:
    key = Fernet.generate_key().decode()
    token = encrypt_result({"status": "completed", "model": "fixture"}, key)
    assert decrypt_result(token, key)["status"] == "completed"
    import pytest
    with pytest.raises(ValueError):
        decrypt_result(token[:-1] + b"x", key)
