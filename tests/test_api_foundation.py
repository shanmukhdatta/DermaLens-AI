"""Actual FastAPI smoke tests against a no-model application instance."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from packages.common.errors import ErrorCode, ModelNotReady
from services.cv.runtime import UnavailableModelRuntime


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(Settings(env="test", public_web_origin="http://localhost:3000")))


def test_liveness_has_contract_shape(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_fails_closed_with_no_checkpoint(client: TestClient) -> None:
    response = client.get("/api/v1/readiness")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_no_unimplemented_sensitive_routes_are_active(client: TestClient) -> None:
    assert client.get("/api/v1/analyses").status_code == 405
    assert client.get("/api/v1/copilot/query").status_code == 404
    assert client.post("/api/v1/analyses").status_code == 401
    assert client.post("/api/v1/copilot/query", json={"question": "hello"}).status_code == 404
    assert client.get("/api/v1/models/current").status_code == 401


def test_no_real_model_fallback() -> None:
    runtime = UnavailableModelRuntime()
    assert runtime.ready is False
    with pytest.raises(ModelNotReady) as exc:
        runtime.predict(None)  # type: ignore[arg-type]
    assert exc.value.code == ErrorCode.MODEL_NOT_READY
    assert exc.value.status_code == 503
    assert exc.value.as_payload()["error"] == {
        "code": "MODEL_NOT_READY",
        "message": "Model inference is not available in this build.",
    }


def test_settings_reject_sensitive_modes() -> None:
    with pytest.raises(ValidationError):
        Settings(env="test", enable_image_storage=True)
    with pytest.raises(ValidationError):
        Settings(env="test", enable_research_image_opt_in=True)
    with pytest.raises(ValidationError):
        Settings(env="production", public_web_origin="http://example.org")


def test_settings_are_typed_and_bound() -> None:
    settings = Settings(env="test", api_port=8000)
    assert settings.api_port == 8000
    with pytest.raises(ValidationError):
        Settings(env="test", api_port=70000)
    with pytest.raises(ValidationError):
        Settings(env="test", public_web_origin="*")
