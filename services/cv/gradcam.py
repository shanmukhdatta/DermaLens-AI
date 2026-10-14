"""Optional Grad-CAM research visualization with explicit model-layer requirements."""
from __future__ import annotations

from importlib import import_module
from typing import Any

import numpy as np


class ExplanationUnavailable(RuntimeError):
    """A valid explanation cannot be generated for this model and image."""


def gradcam_heatmap(
    model: Any,
    batch: np.ndarray,
    *,
    class_index: int,
    convolution_layer_name: str,
) -> np.ndarray:
    """Return normalized activation heatmap, never lesion proof or medical explanation.

    Requires an explicitly chosen convolution feature layer; unsupported architectures
    must not be silently assigned synthetic or unrelated heatmaps.
    """
    if (
        batch.shape != (1, 224, 224, 3)
        or batch.dtype != np.float32
        or not np.isfinite(batch).all()
        or not 0 <= class_index < 6
        or not convolution_layer_name
    ):
        raise ExplanationUnavailable("Unsupported input or class selection")
    try:
        tf = import_module("tensorflow")
        layer = model.get_layer(convolution_layer_name)
        explainer = tf.keras.Model(model.inputs, [layer.output, model.output])
        with tf.GradientTape() as tape:
            feature_maps, predictions = explainer(batch, training=False)
            if (
                len(feature_maps.shape) != 4
                or len(predictions.shape) != 2
                or predictions.shape[-1] != 6
            ):
                raise ExplanationUnavailable("Layer output is incompatible")
            target = predictions[:, class_index]
        gradients = tape.gradient(target, feature_maps)
        if gradients is None:
            raise ExplanationUnavailable("No gradients available")
        weights = tf.reduce_mean(gradients, axis=(0, 1, 2))
        activation = tf.reduce_sum(feature_maps[0] * weights, axis=-1)
        activation = tf.nn.relu(activation)
        arr = np.asarray(activation.numpy(), dtype=np.float32)
        if arr.ndim != 2 or not np.isfinite(arr).all() or arr.size == 0:
            raise ExplanationUnavailable("Invalid feature maps")
        maximum = float(arr.max())
        if maximum <= 1e-12:
            raise ExplanationUnavailable("No class-specific activation")
        return arr / maximum
    except ExplanationUnavailable:
        raise
    except (ImportError, AttributeError, KeyError, TypeError, ValueError) as exc:
        raise ExplanationUnavailable("Explanation not supported by this model") from exc
