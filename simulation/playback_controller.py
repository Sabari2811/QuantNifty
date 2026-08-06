from __future__ import annotations

import time


class PlaybackController:
    """
    Controls automatic replay playback.

    Responsibilities
    ----------------
    • Play
    • Pause
    • Stop
    • Replay speed
    """

    def __init__(self):

        self.playing = False

        self.speed = 1.0

    # ==========================================
    # Controls
    # ==========================================

    def play(self):

        self.playing = True

    def pause(self):

        self.playing = False

    def stop(self):

        self.playing = False

    # ==========================================
    # Helpers
    # ==========================================

    def is_playing(self):

        return self.playing

    def set_speed(self, speed):

        self.speed = speed

    def delay(self):

        time.sleep(1 / self.speed)