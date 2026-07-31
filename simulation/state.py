from dataclasses import dataclass


@dataclass
class SimulationState:
    """
    Current state of a simulation.

    Shared by:
        - Replay
        - Backtesting
        - Walk Forward Testing
    """

    # Simulation status
    running: bool = False
    paused: bool = False
    finished: bool = False

    # Cursor
    current_index: int = 0

    # Playback speed (1x, 2x, ...)
    speed: int = 1

    # Progress
    progress: float = 0.0