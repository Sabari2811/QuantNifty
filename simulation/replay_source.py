from __future__ import annotations

from abc import ABC, abstractmethod

from simulation.replay_snapshot import ReplaySnapshot


class ReplaySource(ABC):
    """
    Base interface for replay data sources.

    Navigation is owned by ReplaySession.
    SimulationProvider only reads the current snapshot.
    """

    @abstractmethod
    def current(self) -> ReplaySnapshot:
        """
        Return current snapshot without changing position.
        """
        pass

    @abstractmethod
    def next(self) -> ReplaySnapshot:
        """
        Advance one snapshot.
        """
        pass

    @abstractmethod
    def previous(self) -> ReplaySnapshot:
        """
        Move back one snapshot.
        """
        pass

    @abstractmethod
    def seek(self, index: int) -> ReplaySnapshot:
        """
        Jump to snapshot index.
        """
        pass

    @abstractmethod
    def has_next(self) -> bool:
        pass

    @abstractmethod
    def has_previous(self) -> bool:
        pass

    @abstractmethod
    def reset(self):
        pass