"""Private offline batch inference: verified Keras model -> leakage-audited research CSV.

Input manifest stays local. No image uploads, data scraping, diagnostic APIs or automatic
model promotion. All outputs are pseudonymized metadata and scores for independent review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import io
import json
import os
import tempfile
import warnings
from pathlib import Path
from typing import Any, Protocol

import numpy as np
from PIL import Image

from services.cv.artifacts import preprocess_compatible
from services.cv.ports import ModelRuntime
from services.cv.quality import ALLOW_FORMATS, MAX_IMAGE_BYTES, MAX_SIDE, MIN_SIDE
from services.learning.evaluation import PROB_COLUMNS, audit_rows, evaluate

INPUT_COLUMNS = frozenset(
    {
        "image_path",
        "example_id",
        "subject_id",
        "split",
        "source",
        "label",
        "skin_tone_group",
        "device_group",
    }
)
OUTPUT_COLUMNS = (
    "example_id",
    "subject_id",
    "content_sha256",
    "split",
    "source",
    "label",
    "model_version",
    "skin_tone_group",
    "device_group",
    *PROB_COLUMNS,
)


class ManifestModel(Protocol):
    @property
    def ready(self) -> bool: ...

    def predict(self, rgb_float32_batch: np.ndarray[Any, np.dtype[np.float32]]) -> Any: ...


def _pseudonym(secret: bytes, purpose: str, value: str) -> str:
    if not value or len(value) > 512:
        raise ValueError("Missing or oversized manifest identifier")
    return hmac.new(secret, (purpose + ":" + value).encode("utf-8"), hashlib.sha256).hexdigest()


def _manifest_records(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or set(reader.fieldnames) != INPUT_COLUMNS:
            raise ValueError("Private input manifest requires the exact eight documented columns")
        rows = [dict(row) for row in reader]
    if not rows or len(rows) > 100000:
        raise ValueError("Manifest has no examples or exceeds the offline batch limit")
    if any(any(value is None for value in row.values()) for row in rows):
        raise ValueError("Manifest contains missing fields")
    return rows


def _bounded_image(image_root: Path, relative_name: str) -> tuple[bytes, np.ndarray[Any, np.dtype[np.float32]]]:
    relative = Path(relative_name)
    if not relative_name or relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Image manifest paths must be relative to the private image root")
    source = (image_root / relative).resolve(strict=True)
    if not source.is_relative_to(image_root) or not source.is_file():
        raise ValueError("Image path escapes the private image root")
    if source.stat().st_size <= 0 or source.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds the bounded byte limit")
    payload = source.read_bytes()
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(payload)) as photo:
            if photo.format not in ALLOW_FORMATS or getattr(photo, "n_frames", 1) != 1:
                raise ValueError("Unsupported image type or animated image")
            if min(photo.size) < MIN_SIDE or max(photo.size) > MAX_SIDE:
                raise ValueError("Image dimensions are unsupported")
            photo.load()
            # Preserve the original research preprocessing; do not silently apply ROI
            # alignment or EXIF reorientation without training/inference parity review.
            batch = preprocess_compatible(photo)
    return payload, batch


def collect_predictions(
    manifest: Path,
    image_root: Path,
    secret: bytes,
    runtime: ModelRuntime,
    ordered_labels: tuple[str, ...],
) -> list[dict[str, str]]:
    """Reject entire batch on corruption/leakage; never silently skip examples."""
    if len(secret) < 32 or not runtime.ready:
        raise ValueError("Require a private 32+-byte key and loaded verified model")
    root = image_root.resolve(strict=True)
    rows: list[dict[str, str]] = []
    model_version: str | None = None
    for record in _manifest_records(manifest):
        payload, tensor = _bounded_image(root, record["image_path"])
        prediction = runtime.predict(tensor)
        if prediction.ordered_labels != ordered_labels:
            raise ValueError("Prediction classes do not match the integrity-verified label map")
        if model_version is None:
            model_version = prediction.model_version
        if prediction.model_version != model_version or not prediction.model_version:
            raise ValueError("Model versions changed during a batch")
        values = np.asarray(prediction.probabilities, dtype=float)
        if (
            values.shape != (6,)
            or not np.isfinite(values).all()
            or np.any(values < 0)
            or np.any(values > 1)
            or not np.isclose(float(values.sum()), 1.0, atol=1e-4)
        ):
            raise ValueError("Invalid classifier probability vector")
        result = {
            "example_id": _pseudonym(secret, "example", record["example_id"]),
            "subject_id": _pseudonym(secret, "subject", record["subject_id"]),
            "content_sha256": hashlib.sha256(payload).hexdigest(),
            "split": record["split"],
            "source": record["source"],
            "label": record["label"],
            "model_version": prediction.model_version,
            "skin_tone_group": record["skin_tone_group"],
            "device_group": record["device_group"],
        }
        result.update({name: format(float(value), ".17g") for name, value in zip(PROB_COLUMNS, values, strict=True)})
        rows.append(result)
    # Subject-level and identical-file leakage checks must succeed BEFORE writing files.
    audit_rows(rows, ordered_labels)
    return rows


def _write_private(path: Path, content: str, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError("Private output exists; pass --overwrite to replace it")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="", dir=path.parent, prefix=".private-", delete=False
        ) as stream:
            temp_path = Path(stream.name)
            os.chmod(temp_path, 0o600)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def write_results(
    rows: list[dict[str, str]],
    ordered_labels: tuple[str, ...],
    predictions_out: Path,
    evaluation_out: Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Evaluate before any write. Contents contain pseudonyms, never paths/photos."""
    if predictions_out.resolve() == evaluation_out.resolve():
        raise ValueError("Predictions and report require distinct output files")
    if not overwrite and (predictions_out.exists() or evaluation_out.exists()):
        raise FileExistsError("Private output already exists")
    report = evaluate(rows, ordered_labels)
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    _write_private(predictions_out, buffer.getvalue(), overwrite=overwrite)
    _write_private(evaluation_out, json.dumps(report, indent=2, sort_keys=True) + "\n", overwrite=overwrite)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True, help="Signed model package manifest")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--input-csv", type=Path, required=True, help="Private metadata + relative image paths")
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--pseudonym-key-file", type=Path, required=True, help="Private key, at least 32 random bytes")
    parser.add_argument("--predictions-out", type=Path, required=True)
    parser.add_argument("--evaluation-out", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    from services.cv.keras_runtime import VerifiedKerasModel

    # The Keras adapter enforces manifest hashes, source provenance and trained label order.
    runtime = VerifiedKerasModel(args.manifest, args.checkpoint, args.label_map)
    secret = args.pseudonym_key_file.read_bytes()
    rows = collect_predictions(
        args.input_csv, args.image_root, secret, runtime, runtime.artifacts.ordered_labels
    )
    report = write_results(
        rows, runtime.artifacts.ordered_labels, args.predictions_out, args.evaluation_out,
        overwrite=args.overwrite,
    )
    print(
        f"Offline examples evaluated: {len(rows)}; held-out test n={report['metrics']['n']}; "
        "clinical validation: false"
    )


if __name__ == "__main__":
    main()
