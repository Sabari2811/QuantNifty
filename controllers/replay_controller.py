from __future__ import annotations

import time
from typing import Optional

from runtime.runtime_manager import RuntimeManager
from simulation.replay_session import ReplaySession


class ReplayController:
    """
    Controls replay execution.

    Responsibilities
    ----------------
    - Replay navigation
    - Playback state
    - Playback speed
    - Runtime orchestration

    UI independent.
    """

    def __init__(
        self,
        runtime_manager: RuntimeManager,
        replay_session: ReplaySession,
    ):

        self.runtime = runtime_manager
        self.session = replay_session

        self._playing = False
        self._speed = 1.0

    # ==========================================================
    # Playback
    # ==========================================================

    def play(self):

        self._playing = True

    def pause(self):

        self._playing = False

    @property
    def is_playing(self):

        return self._playing

    # ==========================================================
    # Navigation
    # ==========================================================

    def next(self):

        if not self.session.has_next():
            return None

        self.session.next()

        return self.runtime.run_once()

    def previous(self):

        if not self.session.has_previous():
            return None

        self.session.previous()

        return self.runtime.run_once()

    def restart(self):

        self.session.reset()

        return self.runtime.run_once()

    def jump_to(self, index: int):

        if index < 0:
            index = 0

        if index >= self.session.total:
            index = self.session.total - 1

        self.session.reset()

        while self.session.index < index:
            self.session.next()

        return self.runtime.run_once()

    # ==========================================================
    # Playback Loop
    # ==========================================================

    def run(self):

        while self._playing and self.session.has_next():

            yield self.next()

            time.sleep(1 / self._speed)

    # ==========================================================
    # Speed
    # ==========================================================

    def set_speed(self, speed: float):

        if speed <= 0:
            raise ValueError("Speed must be positive.")

        self._speed = speed

    @property
    def speed(self):

        return self._speed

    # ==========================================================
    # Runtime
    # ==========================================================

    def current_context(self):

        return self.runtime.get_context()

    def current_progress(self):

        return {
            "current": self.session.index + 1,
            "total": self.session.total,
            "percent": self.session.progress,
        }

    # ==========================================================
    # Helpers
    # ==========================================================

    def has_next(self):

        return self.session.has_next()

    def has_previous(self):

        return self.session.has_previous()