from __future__ import annotations

from pathlib import Path

from simulation.replay_loader import ReplayLoader
from simulation.replay_snapshot import ReplaySnapshot

from simulation.replay_source import ReplaySource



class ReplaySession(ReplaySource):
    """
    Maintains navigation through a sequence of recorded snapshots.

    Responsibilities:
        - Track current position
        - Move forward/backward
        - Reset session
        - Return ReplaySnapshot objects
    """

    def __init__(self, snapshot_folders: list[str | Path]):

        self._folders = [Path(f) for f in snapshot_folders]

        self._loader = ReplayLoader()

        self._index = 0

    # =====================================================
    # Navigation
    # =====================================================

    def has_next(self) -> bool:

        return self._index < len(self._folders)

    def has_previous(self) -> bool:

        return self._index > 0

    def reset(self):

        self._index = 0

    # =====================================================
    # Snapshot Access
    # =====================================================

    def current(self) -> ReplaySnapshot:

        if not self._folders:
            raise RuntimeError("Replay session is empty.")

        return self._loader.load(
            self._folders[self._index]
        )

    def next(self) -> ReplaySnapshot:

        snapshot = self.current()

        if self._index < len(self._folders) - 1:
            self._index += 1

        return snapshot

    def previous(self) -> ReplaySnapshot:

        if self._index > 0:
            self._index -= 1

        return self.current()

    # =====================================================
    # Properties
    # =====================================================

    @property
    def index(self):

        return self._index

    @property
    def total(self):

        return len(self._folders)

    @property
    def progress(self):

        if self.total == 0:
            return 0.0

        return ((self._index + 1) / self.total) * 100

    # =====================================================
    # Random Access
    # =====================================================

    def seek(self, index: int) -> ReplaySnapshot:
        """
        Move directly to a replay position.

        Parameters
        ----------
        index:
            Snapshot index.

        Returns
        -------
        ReplaySnapshot
        """

        if not self._folders:
            raise RuntimeError("Replay session is empty.")

        index = max(0, min(index, self.total - 1))

        self._index = index

        return self.current()