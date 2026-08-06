from __future__ import annotations

from pathlib import Path

from simulation.replay_loader import ReplayLoader
from simulation.replay_snapshot import ReplaySnapshot
from simulation.replay_source import ReplaySource


class ReplaySession(ReplaySource):
    """
    Maintains navigation through a sequence of recorded snapshots.

    Supports BOTH:

        Legacy:
            snapshot_folders = [
                .../000001
                .../000002
            ]

        Session:
            snapshot_folders = [
                .../04-Aug-2026
            ]
    """

    def __init__(
        self,
        snapshot_folders: list[str | Path]
    ):

        self._folders = []

        #
        # Expand session folders into snapshot folders
        #
        for folder in snapshot_folders:

            folder = Path(folder)

            #
            # New session recording
            #
            if (folder / "session.json").exists():

                snapshots = sorted(

                    p
                    for p in folder.iterdir()
                    if (
                        p.is_dir()
                        and
                        (p / "manifest.json").exists()
                    )

                )

                self._folders.extend(snapshots)

            #
            # Legacy recording
            #
            else:

                self._folders.append(folder)

        self._loader = ReplayLoader()

        self._index = 0

    # =====================================================
    # Navigation
    # =====================================================

    def current(self) -> ReplaySnapshot:

        if not self._folders:

            raise RuntimeError(
                "Replay session is empty."
            )

        return self._loader.load(
            self._folders[self._index]
        )

    def next(self) -> ReplaySnapshot:

        if self.has_next():

            self._index += 1

        return self.current()

    def previous(self) -> ReplaySnapshot:

        if self.has_previous():

            self._index -= 1

        return self.current()

    def seek(
        self,
        index: int
    ) -> ReplaySnapshot:

        if not self._folders:

            raise RuntimeError(
                "Replay session is empty."
            )

        index = max(0, min(index, self.total - 1))

        self._index = index

        return self.current()

    def reset(self):

        self._index = 0

    # =====================================================
    # Status
    # =====================================================

    def has_next(self):

        return self._index < self.total - 1

    def has_previous(self):

        return self._index > 0

    @property
    def finished(self):

        return not self.has_next()

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

        return round(

            ((self._index + 1) / self.total) * 100,

            2

        )