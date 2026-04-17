"""Capture Agent — biological simulator for periodic frame acquisition.

Models the temporal illusion of cattle passing through a scale one-by-one.
Each animal enters the camera FOV for `passage_time` seconds, then a gap
of `arrival_time` seconds elapses before the next animal appears.

The TimedBehaviour pulses at the FPS rate.  On each tick it computes the
organic elapsed time since the current animal entered the frame:

- PASSAGE mode  (elapsed <= passage_time):
    Capture a frame, store it in FRAME_BUFFER, and FIPA-INFORM the key
    (plus animal_id and elapsed_time) to the next agent.
- ARRIVAL mode  (passage_time < elapsed < passage_time + arrival_time):
    Idle — the animal is off-screen.  No capture, no message.
- RESTART       (elapsed >= passage_time + arrival_time):
    Advance to the next animal and reset the clock.  If all animals
    have been processed, stop the reactor.

Blocking calls (time.sleep, loops) are prohibited — the Twisted event
loop must never be blocked.
"""

import json
import time
import uuid

from twisted.internet import reactor

import mas  # noqa: F401

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import TimedBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message

from mas.adapters.capture_adapter import CaptureAdapter
from mas.utils.globals import FRAME_BUFFER


class CaptureBehaviour(TimedBehaviour):
    """Pulsing behaviour that drives the PASSAGE / ARRIVAL / RESTART cycle."""

    def __init__(
        self,
        agent: Agent,
        capture_adapter: CaptureAdapter,
        next_agent_aid: str,
        passage_time: int,
        arrival_time: int,
        herd_size: int,
        interval_seconds: float,
    ):
        super().__init__(agent, interval_seconds)
        self.capture_adapter = capture_adapter
        self.next_agent_aid = next_agent_aid
        self.passage_time = passage_time
        self.arrival_time = arrival_time
        self.herd_size = herd_size

        self.current_animal_id = 1
        self.start_at = time.time()
        self._finished = False

    def on_time(self):
        super().on_time()

        if self._finished:
            return

        elapsed = time.time() - self.start_at
        cycle = self.passage_time + self.arrival_time

        # --- RESTART: cycle finished, advance to next animal ---
        if elapsed >= cycle:
            self.current_animal_id += 1
            if self.current_animal_id > self.herd_size:
                self._finished = True
                display_message(
                    self.agent.aid.name,
                    f"[DONE] All {self.herd_size} animals processed. Stopping reactor.",
                )
                reactor.stop()
                return
            self.start_at = time.time()
            display_message(
                self.agent.aid.name,
                f"[RESTART] Animal {self.current_animal_id}/{self.herd_size} entering scale.",
            )
            return

        # --- ARRIVAL mode: animal off-screen, idle ---
        if elapsed > self.passage_time:
            return

        # --- PASSAGE mode: animal is visible, capture and publish ---
        frame_id = str(uuid.uuid4())[:12]
        img = self.capture_adapter.get_frame()
        FRAME_BUFFER[frame_id] = img

        msg = ACLMessage(ACLMessage.INFORM)
        msg.set_ontology("frame-capture")
        msg.add_receiver(AID(self.next_agent_aid))
        msg.set_content(json.dumps({
            "frame_id": frame_id,
            "animal_id": self.current_animal_id,
            "elapsed_time": round(elapsed, 4),
        }, ensure_ascii=True))
        self.agent.send(msg)


class CaptureAgent(Agent):
    """Capture PADE agent — biological simulator that publishes frame keys."""

    def __init__(
        self,
        aid,
        capture_adapter: CaptureAdapter,
        next_agent_aid: str,
        interval_seconds: float = 0.2,
        herd_size: int = 1,
        passage_time: int = 30,
        arrival_time: int = 5,
        debug: bool = False,
    ):
        super().__init__(aid=aid, debug=debug)
        self.capture_adapter = capture_adapter
        self.next_agent_aid = next_agent_aid
        self.interval_seconds = interval_seconds
        self.herd_size = herd_size
        self.passage_time = passage_time
        self.arrival_time = arrival_time

    def on_start(self):
        super().on_start()
        display_message(
            self.agent.aid.name,
            f"CaptureAgent started — herd_size={self.herd_size}, "
            f"passage_time={self.passage_time}s, arrival_time={self.arrival_time}s, "
            f"fps={1/self.interval_seconds:.1f}.",
        )
        self.behaviours.append(CaptureBehaviour(
            agent=self,
            capture_adapter=self.capture_adapter,
            next_agent_aid=self.next_agent_aid,
            passage_time=self.passage_time,
            arrival_time=self.arrival_time,
            herd_size=self.herd_size,
            interval_seconds=self.interval_seconds,
        ))

    def react(self, message):
        super().react(message)
