from simulation.session import SimulationSession


class SimulationController:
    """
    Controls simulation execution.

    Responsibilities
    ----------------
    - Play
    - Pause
    - Resume
    - Stop
    - Reset
    - Next
    - Previous
    - Goto
    """

    def __init__(self, session: SimulationSession):
        self.session = session

    @property
    def state(self):
        return self.session.state

    @property
    def current_index(self):
        """
        Current replay/backtest candle index.
        """
        return self.state.current_index

    # ==========================================================
    # CONTROLS
    # ==========================================================

    def play(self):
        self.state.running = True
        self.state.paused = False
        self.state.finished = False

    def pause(self):
        self.state.paused = True

    def resume(self):
        if self.state.running:
            self.state.paused = False

    def stop(self):
        self.state.running = False
        self.state.paused = False
        self.state.finished = True

    def reset(self):
        self.state.running = False
        self.state.paused = False
        self.state.finished = False

        self.state.current_index = 0
        self.state.progress = 0.0

    # ==========================================================
    # NAVIGATION
    # ==========================================================

    def next(self):
        self.state.current_index += 1

    def previous(self):
        if self.state.current_index > 0:
            self.state.current_index -= 1

    def goto(self, index: int):
        if index >= 0:
            self.state.current_index = index