"""Frame Selection Agent — gatekeeper that evaluates frame suitability.

Receives enhanced frames from DataEnhanceAgent (ontology "frame-enhanced"),
evaluates whether the organic elapsed_time falls within the suitable
window, and either forwards the key to PredictWeightAgent or deletes
the frame from FRAME_BUFFER to free RAM immediately.

The evaluation delegates to FrameSelectionAdapter via deferToThread
because the domain method may include a snooze_duration sleep for
simulated latency parity with the baseline.
"""

import json

from twisted.internet.threads import deferToThread

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.core.agent import Agent
from pade.misc.utility import display_message

from mas.adapters.frame_selection_adapter import FrameSelectionAdapter
from mas.utils.globals import FRAME_BUFFER


class FrameSelectionAgent(Agent):
    """Frame selection PADE agent — suitability gatekeeper with GC."""

    def __init__(
        self,
        aid,
        frame_selection_adapter: FrameSelectionAdapter,
        next_agent_aid: str,
        debug: bool = False,
    ):
        super().__init__(aid=aid, debug=debug)
        self.frame_selection_adapter = frame_selection_adapter
        self.next_agent_aid = next_agent_aid
        self.discarded = 0
        self.forwarded = 0

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

    def _on_evaluation_done(self, result, payload: dict):
        if result:
            self.forwarded += 1
            out = ACLMessage(ACLMessage.INFORM)
            out.set_ontology("frame-selected")
            out.add_receiver(AID(self.next_agent_aid))
            out.set_content(json.dumps(payload, ensure_ascii=True))
            self.send(out)
            display_message(
                self.aid.name,
                f"frame_id={payload['frame_id']} SUITABLE (forwarded). "
                f"metrics: forwarded={self.forwarded} discarded={self.discarded}",
            )
        else:
            self.discarded += 1
            frame_id = payload["frame_id"]
            if frame_id in FRAME_BUFFER:
                del FRAME_BUFFER[frame_id]
            display_message(
                self.aid.name,
                f"frame_id={frame_id} DISCARDED (deleted from buffer). "
                f"metrics: forwarded={self.forwarded} discarded={self.discarded}",
            )

    def _on_evaluation_error(self, failure):
        display_message(
            self.aid.name,
            f"[ERROR] Evaluation failed: {failure.getErrorMessage()}",
        )

    def _schedule_evaluation(self, payload: dict):
        elapsed = payload.get("elapsed_time", 0.0)
        d = deferToThread(self.frame_selection_adapter.evaluate, elapsed)
        d.addCallback(self._on_evaluation_done, payload)
        d.addErrback(self._on_evaluation_error)

    def react(self, message):
        super().react(message)
        if message.performative != ACLMessage.INFORM:
            return
        if message.ontology != "frame-enhanced":
            return
        payload = self._parse_payload(message)
        if not payload:
            return
        self._schedule_evaluation(payload)

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "FrameSelectionAgent started.")
