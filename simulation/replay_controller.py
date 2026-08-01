"""
Replay playback controller.

Coordinates ReplayState and ReplaySession.

The controller contains playback operations only.
It intentionally knows nothing about LiveEngine,
SimulationProvider or Streamlit.
"""

from __future__ import annotations

from simulation.replay_session import ReplaySession
from simulation.replay_state import ReplayState


class ReplayController:
    """
    Controls replay playback.

    Responsibilities
    ----------------
    * Play
    * Pause
    * Stop
    * Navigate
    * Update ReplayState
    """

    def __init__(
        self,
        session: ReplaySession,
        state: ReplayState,
    ) -> None:

        self._session = session
        self._state = state

        self._state.total_cycles = session.total

    # -----------------------------------------------------
    # Playback
    # -----------------------------------------------------

    def play(self) -> None:

        self._state.is_playing = True
        self._state.paused = False

    def pause(self) -> None:

        self._state.is_playing = False
        self._state.paused = True

    def stop(self) -> None:

        self._session.reset()
        self._state.reset()

        self._state.total_cycles = self._session.total

    # -----------------------------------------------------
    # Navigation
    # -----------------------------------------------------

    def next(self):

        snapshot = self._session.next()

        self._state.update(
            cycle=self._session.index,
            timestamp=snapshot.timestamp,
        )

        return snapshot

    def previous(self):

        snapshot = self._session.previous()

        self._state.update(
            cycle=self._session.index,
            timestamp=snapshot.timestamp,
        )

        return snapshot

    def seek(self, index: int):

        snapshot = self._session.seek(index)

        self._state.update(
            cycle=self._session.index,
            timestamp=snapshot.timestamp,
        )

        return snapshot
    # -----------------------------------------------------
    # Settings
    # -----------------------------------------------------

    def set_speed(self, speed: int):

        if speed < 1:
            raise ValueError("Replay speed must be >= 1.")

        self._state.speed = speed

    # -----------------------------------------------------
    # Properties
    # -----------------------------------------------------

    @property
    def state(self) -> ReplayState:

        return self._state