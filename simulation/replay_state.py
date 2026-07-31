"""
Replay state for the QuantNifty Replay Engine.

This module contains only the mutable playback state.
It intentionally has no knowledge of ReplaySession,
SimulationProvider, LiveEngine or Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ReplayState:
    """Holds the current replay playback state."""

    current_cycle: int = 0
    total_cycles: int = 0

    speed: int = 1

    is_playing: bool = False
    paused: bool = False
    finished: bool = False

    current_timestamp: datetime | None = None

    @property
    def progress(self) -> float:
        """
        Returns replay progress as a percentage (0-100).

        Returns:
            float: Replay completion percentage.
        """
        if self.total_cycles <= 0:
            return 0.0

        return round((self.current_cycle / self.total_cycles) * 100, 2)

    def reset(self) -> None:
        """Reset replay state."""

        self.current_cycle = 0
        self.speed = 1

        self.is_playing = False
        self.paused = False
        self.finished = False

        self.current_timestamp = None

    def update(
        self,
        *,
        cycle: int,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Update replay position.

        Parameters
        ----------
        cycle:
            Current replay cycle.

        timestamp:
            Snapshot timestamp.
        """

        self.current_cycle = cycle
        self.current_timestamp = timestamp

        if self.total_cycles > 0:
            self.finished = self.current_cycle >= self.total_cycles