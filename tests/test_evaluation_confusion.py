"""Full six-class research confusion matrix with explicit absent-class semantics."""
from __future__ import annotations

import numpy as np

from services.learning.evaluation import PROB_COLUMNS, _stats

LABELS = (
    "Acne", "Fungal Infection", "Hyperpigmentation",
    "Normal Skin", "Skin Cancer", "Vitiligo",
)


def row(true_index: int, predicted_index: int) -> dict[str, str]:
    probabilities = np.full(6, 0.02, dtype=float)
    probabilities[predicted_index] = 0.90
    return {
        "label": LABELS[true_index],
        **{key: str(value) for key, value in zip(PROB_COLUMNS, probabilities, strict=True)},
    }


def test_confusion_matrix_labels_orientation_and_specificity() -> None:
    records = [row(i, i) for i in range(6) for _ in range(2)]
    # One real acne observation is incorrectly assigned skin cancer.
    records[0] = row(0, 4)
    # One real normal observation is incorrectly assigned acne.
    records[6] = row(3, 0)
    report = _stats(records, LABELS)
    matrix = report["confusion_matrix"]
    assert matrix["labels"] == list(LABELS)
    assert matrix["rows_are"] == "actual"
    assert matrix["columns_are"] == "predicted"
    assert sum(sum(values) for values in matrix["counts"]) == 12
    assert matrix["counts"][0][4] == 1
    assert matrix["counts"][3][0] == 1
    acne = report["per_class"]["Acne"]
    assert acne["true_positive"] == 1
    assert acne["false_positive"] == 1
    assert acne["false_negative"] == 1
    assert acne["true_negative"] == 9
    assert acne["sensitivity"] == 0.5
    assert acne["specificity"] == 0.9
    assert report["accuracy"] == round(10 / 12, 5)


def test_missing_class_has_unmeasurable_sensitivity() -> None:
    report = _stats([row(0, 0), row(1, 1)], LABELS)
    result = report["per_class"]["Skin Cancer"]
    assert result["support"] == 0
    assert result["sensitivity"] is None
    assert result["specificity"] == 1.0
    assert report["confusion_matrix"]["counts"][4] == [0] * 6


def test_all_single_class_has_unmeasurable_specificity() -> None:
    report = _stats([row(0, 0), row(0, 0)], LABELS)
    assert report["per_class"]["Acne"]["sensitivity"] == 1.0
    assert report["per_class"]["Acne"]["specificity"] is None
