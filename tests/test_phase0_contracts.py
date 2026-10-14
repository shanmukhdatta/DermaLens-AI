"""Phase 0 tests for contract shape, never a substitute for runtime inference tests."""

from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from scripts.validate_phase0 import API, MODEL_SCHEMA, ROOT, validate_all


def test_phase0_docs_and_contracts() -> None:
    assert validate_all() == []


def test_manifest_refuses_wrong_preprocessing_and_incomplete_hash() -> None:
    schema = json.loads(MODEL_SCHEMA.read_text(encoding="utf-8"))
    good = {
        "schema_version": "1",
        "model_id": "fixture-only-not-a-trained-model",
        "version": "0.0.0",
        "status": "candidate",
        "source_repository": "https://github.com/shanmukhdatta/Facial_Skin_Diesease",
        "source_commit": "a" * 40,
        "framework": {
            "name": "tensorflow-keras",
            "python_version": "3.x",
            "tensorflow_version": "fixture",
            "keras_version": "fixture",
        },
        "checkpoint": {"uri": "fixture-only", "filename": "fixture.keras", "sha256": "a" * 64},
        "label_map": {
            "uri": "fixture-only",
            "filename": "label_map.json",
            "sha256": "b" * 64,
            "count": 6,
            "format": "index-to-class-json",
        },
        "input": {
            "shape": [None, 224, 224, 3],
            "color_space": "RGB",
            "dtype": "float32",
            "pixel_min": 0,
            "pixel_max": 255,
            "resize": "PIL_BILINEAR",
            "normalization": "model_internal",
        },
        "output": {"kind": "softmax_probabilities", "shape": [None, 6], "class_count": 6},
        "custom_objects": [],
        "preprocessing_version": "fixture-only",
    }
    validator = Draft202012Validator(schema)
    assert validator.is_valid(good)
    bad = json.loads(json.dumps(good))
    bad["input"]["normalization"] = "imagenet_external"
    assert not validator.is_valid(bad)
    bad = json.loads(json.dumps(good))
    bad["checkpoint"]["sha256"] = "unknown"
    assert not validator.is_valid(bad)


def test_openapi_references_research_only_disclaimer_and_no_image_chat() -> None:
    api = json.loads(API.read_text(encoding="utf-8"))
    assert "not medical diagnosis" in api["info"]["description"]
    chat_body = api["paths"]["/api/v1/copilot/query"]["post"]["requestBody"]
    assert chat_body["content"]["application/json"]["schema"]["$ref"].endswith("/CopilotRequest")
    chat_request = api["components"]["schemas"]["CopilotRequest"]["properties"]
    assert list(chat_request) == ["question"]
    assert (ROOT / "README.md").is_file()


def test_phase_tracker_has_fourteen_phases() -> None:
    text = (ROOT / "docs/PHASE_TRACKER.md").read_text(encoding="utf-8")
    for i in range(14):
        assert f"| {i} |" in text
