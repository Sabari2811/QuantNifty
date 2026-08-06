from __future__ import annotations

from engine.replay_engine import ReplayEngine

from providers.simulation_provider import SimulationProvider
from runtime.runtime_mode import RuntimeMode

from simulation.replay_controller import ReplayController
from simulation.replay_state import ReplayState
from simulation.replay_session import ReplaySession

from simulation.playback_controller import PlaybackController



class ReplayFacade:
    """
    High-level Replay API used by Streamlit.

    Owns:

        • ReplaySession
        • ReplayController
        • SimulationProvider
        • ReplayEngine

    The UI talks ONLY to ReplayFacade.
    """

    def __init__(self):

        self.controller = None

        self.provider = None

        self.engine = None

        self.playback = PlaybackController()

    # ==========================================================
    # Load Session
    # ==========================================================

    def load(self, recording):

        session = ReplaySession(

            snapshot_folders=[

                recording.folder

            ]

        )

        state = ReplayState()

        self.controller = ReplayController(

            session=session,

            state=state

        )

        self.provider = SimulationProvider(

            replay_source=session,

            runtime_mode=RuntimeMode.REPLAY_FAST

        )

        self.engine = ReplayEngine(

            self.provider

        )

        self.playback.stop()

        #
        # Render first snapshot.
        #
        return self.engine.run_cycle()

    # ==========================================================
    # Navigation
    # ==========================================================

    def next(self):

        if self.engine is None:

            return None

        if self.controller.state.finished:

            return self.engine.get_context()

        self.controller.next()

        return self.engine.run_cycle()

    def previous(self):

        if self.engine is None:

            return None

        self.controller.previous()

        return self.engine.run_cycle()

    def seek(self, index: int):

        if self.engine is None:

            return None

        self.controller.seek(index)

        return self.engine.run_cycle()

    # ==========================================================
    # Playback
    # ==========================================================

    def play(self):

        if self.controller:

            self.controller.play()

    def pause(self):

        if self.controller:

            self.controller.pause()

    def stop(self):

        if self.controller:

            self.controller.stop()

        if self.engine:

            return self.engine.run_cycle()

    # ==========================================================
    # Context
    # ==========================================================

    def context(self):

        if self.engine is None:

            return None

        return self.engine.get_context()

    # ==========================================================
    # Helpers
    # ==========================================================

    @property
    def loaded(self):

        return self.engine is not None

    @property
    def state(self):

        if self.controller is None:

            return None

        return self.controller.state