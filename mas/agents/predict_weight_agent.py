"""Predict Weight Agent — runs model inference via InferenceAdapter.

Receives suitable frames from FrameSelectionAgent (ontology "frame-selected"),
pops the enhanced image from FRAME_BUFFER to prevent RAM accumulation,
and runs TensorFlow inference in a delegated thread (deferToThread) so
the Twisted event loop is never blocked.

Logs per-animal prediction metrics that mirror the baseline output for
direct scientific comparison.
"""

import json

from twisted.internet.threads import deferToThread

from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.utility import display_message

from mas.adapters.inference_adapter import InferenceAdapter
from mas.utils.globals import FRAME_BUFFER


class PredictWeightAgent(Agent):
    """Prediction PADE agent — runs weight inference off the event loop."""

    def __init__(
        self,
        aid,
        inference_adapter: InferenceAdapter,
        debug: bool = False,
    ):
        super().__init__(aid=aid, debug=debug)
        self.inference_adapter = inference_adapter
        self._predictions: dict[int, list[float]] = {}
        self._total_inferences = 0

    def _parse_payload(self, message) -> dict | None:
        try:
            payload = json.loads(message.content)
        except (TypeError, json.JSONDecodeError):
            display_message(self.aid.name, "[WARN] invalid JSON payload")
            return None
        if not payload.get("frame_id"):
            display_message(self.aid.name, "[WARN] missing frame_id")
            return None
        return payload

    def _on_inference_success(self, result, payload: dict):
        self._total_inferences += 1
        animal_id = payload.get("animal_id", "?")
        frame_id = payload.get("frame_id", "?")
        elapsed = payload.get("elapsed_time", 0.0)
        weight = float(result[0][0]) if result is not None else None

        if animal_id not in self._predictions:
            self._predictions[animal_id] = []
        self._predictions[animal_id].append(weight)

        display_message(
            self.aid.name,
            f"[PREDICTION #{self._total_inferences}] animal_id={animal_id} "
            f"frame_id={frame_id} elapsed_time={elapsed}s weight={weight:.4f} kg",
        )

    def _on_inference_error(self, failure):
        display_message(
            self.aid.name,
            f"[ERROR] Inference failed: {failure.getErrorMessage()}",
        )

    def _schedule_inference(self, payload: dict):
        frame_id = payload["frame_id"]
        img = FRAME_BUFFER.pop(frame_id, None)
        if img is None:
            display_message(self.aid.name, f"[WARN] frame_id={frame_id} not in buffer")
            return

        d = deferToThread(self.inference_adapter.predict, [img])
        d.addCallback(self._on_inference_success, payload)
        d.addErrback(self._on_inference_error)

    def react(self, message):
        super().react(message)
        if message.performative != ACLMessage.INFORM:
            return
        if message.ontology != "frame-selected":
            return
        payload = self._parse_payload(message)
        if not payload:
            return
        self._schedule_inference(payload)

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "PredictWeightAgent started.")

    def get_predictions_summary(self) -> dict:
        """Return per-animal prediction summaries (mean weights)."""
        import numpy as np
        summary = {}
        for aid, weights in self._predictions.items():
            summary[aid] = {
                "n_predictions": len(weights),
                "mean_weight": round(float(np.mean(weights)), 4),
                "weights": weights,
            }
        return summary
