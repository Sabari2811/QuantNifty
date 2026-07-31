from __future__ import annotations

from abc import ABC, abstractmethod

from simulation.replay_snapshot import ReplaySnapshot


class ReplaySource(ABC):
    """
    Base interface for replay data sources.

    Implementations:
        - ReplaySession
        - CSVReplaySource (future)
        - DatabaseReplaySource (future)
        - MonteCarloReplaySource (future)
    """

    @abstractmethod
    def has_next(self) -> bool:
        pass

    @abstractmethod
    def next(self) -> ReplaySnapshot:
        pass

    @abstractmethod
    def reset(self):
        pass