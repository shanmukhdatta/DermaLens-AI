"""Docs allowlist, retrieval provenance, auth, refusal and provider adapter tests."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from apps.api.dermalens_api.routers.copilot import get_docs_provider
from packages.security.identity import Principal
from services.rag.grok import GrokResponseProvider
from services.rag.index import DocChunk, DocumentationIndex


class TestIdentity:
    def verify_bearer(self, token: str) -> Principal:
        assert token == "fixture"
        return Principal(subject="user", issuer="https://test.example/")


class TestProvider:
    calls = 0

    async def generate(self, question: str, excerpts: list[DocChunk]) -> str:
        self.calls += 1
        assert question
        assert excerpts and all(chunk.source.startswith(("README", "docs/")) for chunk in excerpts)
        return "The documents describe versioned model contracts and privacy boundaries."


def test_docs_allowlist_and_retrieval() -> None:
    index = DocumentationIndex.from_repository(Path("."))
    assert len(index.chunks) >= 10
    matches = index.search("model preprocessing RGB float32 224")
    assert matches
    assert all(
        chunk.source.split("#")[0]
        in {
            "README.md",
            *[
                name
                for name in (
                    "docs/01_SYSTEM_ARCHITECTURE.md",
                    "docs/02_COMPUTER_VISION_PIPELINE.md",
                    "docs/03_MODEL_AND_RESEARCH.md",
                    "docs/04_BACKEND_ARCHITECTURE.md",
                    "docs/05_RAG_ASSISTANT.md",
                    "docs/06_FEEDBACK_AND_CONTINUAL_LEARNING.md",
                    "docs/07_MLOPS_AND_DEPLOYMENT.md",
                    "docs/08_API_AND_DATA_FLOW.md",
                    "docs/09_PRIVACY_AND_SAFETY.md",
                )
            ],
        }
        for chunk in matches
    )


def test_docs_endpoint_auth_refusal_and_real_provenance() -> None:
    app = create_app(Settings(env="test", enable_rag_assistant=True, grok_api_key="fake-in-tests"))
    app.dependency_overrides[get_identity_verifier] = lambda: TestIdentity()
    provider = TestProvider()
    app.dependency_overrides[get_docs_provider] = lambda: provider
    with TestClient(app, raise_server_exceptions=False) as client:
        assert (
            client.post(
                "/api/v1/copilot/query", json={"question": "what model is used"}
            ).status_code
            == 401
        )
        headers = {"Authorization": "Bearer fixture"}
        answer = client.post(
            "/api/v1/copilot/query",
            json={"question": "what model preprocessing is used"},
            headers=headers,
        )
        assert answer.status_code == 200
        assert answer.json()["sources"]
        assert provider.calls == 1
        medical = client.post(
            "/api/v1/copilot/query",
            json={"question": "which cream should I use for my face"},
            headers=headers,
        )
        assert medical.status_code == 200
        assert medical.json()["sources"] == []
        assert provider.calls == 1
        assert (
            client.post(
                "/api/v1/copilot/query", json={"question": "a"}, headers=headers
            ).status_code
            == 422
        )


def test_provider_sends_store_false(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: list[object] = []

    class FakeClient:
        async def __aenter__(self) -> FakeClient:
            return self

        async def __aexit__(self, *args: object) -> None:
            pass

        async def post(
            self, url: str, *, headers: dict[str, str], json: dict[str, object]
        ) -> httpx.Response:
            observed.append(json)
            return httpx.Response(
                200,
                json={
                    "output": [
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": "Grounded."}],
                        }
                    ]
                },
                request=httpx.Request("POST", url),
            )

    monkeypatch.setattr("services.rag.grok.httpx.AsyncClient", lambda **kwargs: FakeClient())
    answer = asyncio.run(
        GrokResponseProvider("fixture-only").generate(
            "How does preprocessing work?",
            [DocChunk("README.md#preprocessing", "Preprocessing", "RGB 224")],
        )
    )
    assert answer == "Grounded."
    assert isinstance(observed[0], dict)
    assert observed[0]["store"] is False
    assert "tools" in observed[0] and observed[0]["tools"] == []
