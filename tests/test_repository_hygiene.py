"""Regression tests for version-controlled sensitive paths."""

from __future__ import annotations

from scripts.check_repository_hygiene import forbidden_tracked_path


def test_configuration_examples_are_allowed() -> None:
    assert forbidden_tracked_path(".env.example") is False
    assert forbidden_tracked_path("apps/web/.env.example") is False


def test_sensitive_paths_are_blocked() -> None:
    for path in (
        ".env",
        ".env.local",
        "apps/web/.env.production",
        "data/person.jpg",
        "uploads/subject.png",
        "models/real.keras",
        "keys/auth.pem",
        "artifacts/model.onnx",
        "apps/web/node_modules/index.js",
        "research/id_rsa",
    ):
        assert forbidden_tracked_path(path) is True


def test_original_source_modules_are_not_mistaken_for_private_datasets() -> None:
    assert forbidden_tracked_path("research/legacy/src/data/dataset.py") is False
    assert forbidden_tracked_path("research/legacy/src/data/__init__.py") is False
    assert forbidden_tracked_path("research/legacy/src/data/patient.jpg") is True
    assert forbidden_tracked_path("research/legacy/src/data/secret.env") is True
    assert forbidden_tracked_path("research/legacy/data/patient.py") is True
