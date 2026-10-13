"""Phase 2 black-box security, contract, middleware and dependency tests."""

from __future__ import annotations

import json
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jsonschema import validate
from pydantic import ValidationError

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.dependencies import get_identity_verifier
from apps.api.dermalens_api.main import create_app
from apps.api.dermalens_api.readiness import ReadinessGates
from packages.common.errors import DomainError, ErrorCode
from packages.security.identity import Principal, ensure_owner
from services.cv.runtime import UnavailableModelRuntime


@pytest.fixture
def application() -> FastAPI:
    return create_app(Settings(env="test", public_web_origin="http://localhost:3000"))


@pytest.fixture
def client(application: FastAPI) -> TestClient:
    return TestClient(application, raise_server_exceptions=False)


def test_public_liveness_and_readiness_keep_phase0_shapes(client: TestClient) -> None:
    assert client.get("/api/v1/health").json() == {"status": "ok"}
    response = client.get("/api/v1/readiness")
    assert response.status_code == 503
    assert response.json() == {"status": "not_ready"}


def test_public_operations_do_not_depend_on_identity(client: TestClient) -> None:
    for endpoint in ("/api/v1/health", "/api/v1/readiness"):
        assert client.get(endpoint).status_code in {200, 503}


def test_request_ids_are_canonical_and_consistent(client: TestClient) -> None:
    original = str(uuid4())
    response = client.get("/api/v1/models/current", headers={"X-Request-ID": original})
    assert response.headers["X-Request-ID"] == original
    assert response.json()["request_id"] == original


@pytest.mark.parametrize("unsafe", ["evil", "0" * 600, "f" * 32, "{abc}", ""])
def test_invalid_request_id_is_replaced(client: TestClient, unsafe: str) -> None:
    result = client.get("/missing", headers={"X-Request-ID": unsafe})
    assigned = result.headers["X-Request-ID"]
    UUID(assigned)
    assert assigned != unsafe
    assert result.json()["request_id"] == assigned


def test_missing_route_and_method_use_typed_errors(client: TestClient) -> None:
    missing = client.get("/secret?token=must-not-echo")
    assert missing.status_code == 404
    assert missing.json()["error"] == {
        "code": "NOT_FOUND",
        "message": "Resource not found.",
    }
    assert "must-not-echo" not in missing.text
    method = client.post("/api/v1/health")
    assert method.status_code == 405
    assert method.json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_validation_errors_never_echo_request_values(application: FastAPI) -> None:
    @application.get("/__probe/{age}")
    def probe(age: int) -> dict[str, int]:
        return {"age": age}

    with TestClient(application, raise_server_exceptions=False) as test_client:
        response = test_client.get("/__probe/token-secret-raw")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
    assert "token-secret-raw" not in response.text


def test_domain_errors_use_fixed_messages_not_internal_details(application: FastAPI) -> None:
    @application.get("/__private_domain")
    def private_domain() -> None:
        raise DomainError(ErrorCode.RAG_UNAVAILABLE, "private-api-key-in-exception", 503)

    with TestClient(application, raise_server_exceptions=False) as test_client:
        response = test_client.get("/__private_domain")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "RAG_UNAVAILABLE"
    assert "private-api-key-in-exception" not in response.text


def test_unhandled_errors_are_generic_and_correlated(application: FastAPI) -> None:
    @application.get("/__private_error")
    def private_error() -> None:
        raise RuntimeError("do-not-echo-my-secret")

    with TestClient(application, raise_server_exceptions=False) as test_client:
        response = test_client.get("/__private_error")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "do-not-echo-my-secret" not in response.text
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


@pytest.mark.parametrize("authorization", [None, "Basic foo", "Bearer ", "Bearer not-verified"])
def test_private_route_rejects_unverified_identity(
    client: TestClient, authorization: str | None
) -> None:
    headers = {} if authorization is None else {"Authorization": authorization}
    response = client.get("/api/v1/models/current", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NOT_AUTHORIZED"


class _TestOnlyVerifier:
    """Not imported or configured by application code."""

    def verify_bearer(self, token: str) -> Principal:
        if token != "fixture-only":
            raise AssertionError("Unexpected test token")
        return Principal(subject="test-user", issuer="test-issuer")


def test_private_metadata_requires_injected_verified_actor(application: FastAPI) -> None:
    application.dependency_overrides[get_identity_verifier] = lambda: _TestOnlyVerifier()
    with TestClient(application) as test_client:
        response = test_client.get(
            "/api/v1/models/current", headers={"Authorization": "Bearer fixture-only"}
        )
    assert response.status_code == 200
    assert response.json() == {"ready": False, "model_id": None, "model_version": None}


def test_owner_guard_keeps_other_users_indistinguishable_from_missing() -> None:
    principal = Principal(subject="alpha", issuer="test")
    ensure_owner(principal, "alpha")
    with pytest.raises(DomainError) as denied:
        ensure_owner(principal, "beta")
    assert denied.value.status_code == 404
    assert denied.value.code == ErrorCode.NOT_FOUND


def test_readiness_default_and_missing_policy_fail_closed(application: FastAPI) -> None:
    assert not application.state.readiness_gates.ready()
    application.state.readiness_gates = ReadinessGates(
        model_runtime=UnavailableModelRuntime(), policy_validated=True
    )
    with TestClient(application) as test_client:
        assert test_client.get("/api/v1/readiness").status_code == 503


class _FixtureRuntime:
    @property
    def ready(self) -> bool:
        return True

    def predict(self, rgb_float32_batch: object) -> None:
        raise AssertionError("No inference in the test")


def test_injected_gate_predicate_is_required() -> None:
    runtime = _FixtureRuntime()
    assert not ReadinessGates(model_runtime=runtime).ready()  # type: ignore[arg-type]
    closed = ReadinessGates(
        model_runtime=runtime,  # type: ignore[arg-type]
        policy_validated=True,
        required_checks=(lambda: False,),
    )
    assert not closed.ready()


def test_check_exception_fails_closed() -> None:
    def failing_check() -> bool:
        raise RuntimeError("secret dependency detail")

    gates = ReadinessGates(
        model_runtime=_FixtureRuntime(),  # type: ignore[arg-type]
        policy_validated=True,
        required_checks=(failing_check,),
    )
    assert not gates.ready()


def test_private_and_image_features_remain_unimplemented(client: TestClient) -> None:
    assert client.post("/api/v1/analyses").status_code == 404
    assert client.get("/api/v1/analyses").status_code == 404
    assert client.post("/api/v1/copilot/query", json={"question": "test"}).status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_safe_security_headers_are_on_all_responses(client: TestClient) -> None:
    for target in ("/api/v1/health", "/api/v1/readiness", "/api/v1/models/current", "/missing"):
        response = client.get(target)
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "no-referrer"
        assert response.headers["Cache-Control"] == "no-store"
        assert "default-src 'none'" in response.headers["Content-Security-Policy"]
        assert "Strict-Transport-Security" not in response.headers


def test_production_has_hsts() -> None:
    application = create_app(Settings(env="production", public_web_origin="https://app.example.org"))
    with TestClient(application) as test_client:
        response = test_client.get("/api/v1/health")
    assert response.headers["Strict-Transport-Security"].startswith("max-age=31536000")


def test_cors_allows_only_configured_origin(client: TestClient) -> None:
    allowed = client.options(
        "/api/v1/models/current",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "access-control-allow-credentials" not in allowed.headers
    denied = client.options(
        "/api/v1/models/current",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "https://*.example.com",
        "https://evil.test/path",
        "https://user:pass@example.com",
        "https://example.com?access=1",
        "https://example.com#frag",
        "http://remote.example.com",
        "https://example.com:99999",
    ],
)
def test_reject_unsafe_cors_origin(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(env="test", public_web_origin=origin)


def test_sensitive_storage_is_still_forbidden() -> None:
    with pytest.raises(ValidationError):
        Settings(env="test", enable_image_storage=True)


def test_operational_responses_match_phase0_machine_contract(client: TestClient) -> None:
    with open("packages/contracts/openapi.v1.json", encoding="utf-8") as fh:
        schema = json.load(fh)["components"]["schemas"]["HealthStatus"]
    for route in ("/api/v1/health", "/api/v1/readiness"):
        validate(instance=client.get(route).json(), schema=schema)
