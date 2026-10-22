"""Documentation lookup must be grounded, bounded and independent of Grok keys."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from services.rag.index import ALLOWED_DOCS


def test_docs_lookup_uses_allowlisted_sources() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        response = client.get("/api/v1/docs/search", params={"q": "model preprocessing input"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "matches"
        assert len(payload["matches"]) <= 3
        for excerpt in payload["matches"]:
            assert excerpt["path"] in ALLOWED_DOCS
            assert len(excerpt["excerpt"]) <= 650
        assert "not medical advice" in payload["notice"]


def test_docs_lookup_does_not_unlock_model_inference() -> None:
    app = create_app(Settings(env="test"))
    with TestClient(app) as client:
        assert client.get("/api/v1/readiness").status_code == 503
        assert client.post("/api/v1/analyses").status_code == 401
        assert client.get(
            "/api/v1/docs/search", params={"q": "zzzzqwertyunknownphrase"}
        ).json()["matches"] == []
        assert client.get("/api/v1/docs/search", params={"q": "no"}).status_code == 422
        assert client.get("/api/v1/docs/search", params={"q": "A" * 200}).status_code == 422
        result = client.get("/api/v1/docs/search", params={"q": "RAG retrieval"})
        assert result.headers["Cache-Control"] == "no-store"
