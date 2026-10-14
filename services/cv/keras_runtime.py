"""Verified Keras research model adapter; never silently substitute fake inference."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from services.cv.artifacts import VerifiedArtifacts, verify_artifacts
from services.cv.ports import RawPrediction


def custom_objects_for(tf: Any) -> dict[str, Any]:
    """Reproduce the research repository's serialized custom layer definitions."""

    @tf.keras.saving.register_keras_serializable(package="custom_preprocessing")
    class ResNet50Preprocess(tf.keras.layers.Layer):  # type: ignore[misc]
        def call(self, x: Any) -> Any:
            return tf.keras.applications.resnet50.preprocess_input(x)

    @tf.keras.saving.register_keras_serializable(package="custom_preprocessing")
    class DenseNet121Preprocess(tf.keras.layers.Layer):  # type: ignore[misc]
        def call(self, x: Any) -> Any:
            return tf.keras.applications.densenet.preprocess_input(x)

    @tf.keras.saving.register_keras_serializable(package="custom_preprocessing")
    class ViTPreprocess(tf.keras.layers.Layer):  # type: ignore[misc]
        def call(self, x: Any) -> Any:
            return (tf.cast(x, tf.float32) / 127.5) - 1.0

    @tf.keras.saving.register_keras_serializable(package="custom_preprocessing")
    class ExtractCLSToken(tf.keras.layers.Layer):  # type: ignore[misc]
        def call(self, x: Any) -> Any:
            return x[:, 0, :]

    @tf.keras.saving.register_keras_serializable(package="custom_losses")
    class FocalLoss(tf.keras.losses.Loss):  # type: ignore[misc]
        def __init__(
            self, gamma: float = 2.0, alpha: float = 0.25, name: str = "focal_loss", **kwargs: Any
        ) -> None:
            super().__init__(name=name, **kwargs)
            self.gamma = float(gamma)
            self.alpha = float(alpha)

        def call(self, y_true: Any, y_pred: Any) -> Any:
            labels = tf.cast(tf.reshape(y_true, [-1]), tf.int32)
            predictions = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-7, 1 - 1e-7)
            one_hot = tf.one_hot(labels, depth=tf.shape(predictions)[-1], dtype=tf.float32)
            pt = tf.reduce_sum(one_hot * predictions, axis=-1)
            focal = self.alpha * tf.pow(1.0 - pt, self.gamma) * -tf.math.log(pt)
            return tf.reduce_mean(focal)

        def get_config(self) -> dict[str, Any]:
            return {**super().get_config(), "gamma": self.gamma, "alpha": self.alpha}

    return {
        "ResNet50Preprocess": ResNet50Preprocess,
        "DenseNet121Preprocess": DenseNet121Preprocess,
        "ViTPreprocess": ViTPreprocess,
        "ExtractCLSToken": ExtractCLSToken,
        "FocalLoss": FocalLoss,
    }


class VerifiedKerasModel:
    def __init__(self, manifest_path: Path, checkpoint_path: Path, label_map_path: Path) -> None:
        artifacts = verify_artifacts(manifest_path, checkpoint_path, label_map_path)
        # Lazy TF import: normal API remains available with no checkpoint or GPU.
        tf = import_module("tensorflow")

        self.artifacts: VerifiedArtifacts = artifacts
        model = tf.keras.models.load_model(
            str(artifacts.checkpoint_path),
            custom_objects=custom_objects_for(tf),
            compile=False,
            safe_mode=True,
        )
        if tuple(model.input_shape[1:]) != (224, 224, 3) or tuple(model.output_shape[1:]) != (6,):
            raise ValueError("Trained model tensor shapes do not match manifest")
        self.model = model

    @property
    def ready(self) -> bool:
        return True

    def predict(self, rgb_float32_batch: NDArray[np.float32]) -> RawPrediction:
        if (
            not isinstance(rgb_float32_batch, np.ndarray)
            or rgb_float32_batch.shape != (1, 224, 224, 3)
            or rgb_float32_batch.dtype != np.float32
            or not np.isfinite(rgb_float32_batch).all()
            or rgb_float32_batch.min() < 0
            or rgb_float32_batch.max() > 255
        ):
            raise ValueError("Incompatible model input batch")
        values = np.asarray(self.model.predict(rgb_float32_batch, verbose=0), dtype=float)
        if (
            values.shape != (1, 6)
            or not np.isfinite(values).all()
            or np.any(values < 0)
            or np.any(values > 1)
            or not np.isclose(np.sum(values), 1.0, rtol=1e-3, atol=1e-3)
        ):
            raise ValueError("Classifier produced an invalid probability distribution")
        return RawPrediction(
            model_id=self.artifacts.model_id,
            model_version=self.artifacts.version,
            ordered_labels=self.artifacts.ordered_labels,
            probabilities=tuple(float(v) for v in values[0]),
        )
