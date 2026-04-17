"""Adapter for the PredictWeight domain module.

Bridges the MAS layer to the untouched domain inference logic.
"""

import numpy as np
from typing import Any

from domain.modules.predict_weight import PredictWeight


class InferenceAdapter:
    """Thin wrapper around domain PredictWeight."""

    def __init__(self, model: Any) -> None:
        self._predictor = PredictWeight(model)

    def predict(self, imgs: list) -> np.ndarray:
        return self._predictor.predict(imgs)
