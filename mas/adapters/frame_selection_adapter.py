"""Adapter for the FrameSelection domain module.

Bridges the MAS layer to the untouched domain frame selection logic.
"""

from domain.modules.frame_selection import FrameSelection


class FrameSelectionAdapter:
    """Thin wrapper around domain FrameSelection."""

    def __init__(self, suitable_window: float, snooze_duration: float) -> None:
        self._selection = FrameSelection(suitable_window, snooze_duration)

    def evaluate(self, elapsed_time: float) -> bool:
        return self._selection.evaluate(elapsed_time)
