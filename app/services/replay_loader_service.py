from pathlib import Path

from simulation.replay_session import ReplaySession


class ReplayLoaderService:
    """
    Converts a ReplayRecording into an active ReplaySession.

    Supports:

        • Legacy recordings
        • Session recordings
    """

    def load(self, recording):

        folder = Path(recording.folder)

        #
        # ------------------------------------------------------
        # New Session Format
        #
        # data/snapshots/
        #   02-Aug-2026/
        #       session.json
        #       000001_...
        #       000002_...
        #       ...
        # ------------------------------------------------------
        #
        if (folder / "session.json").exists():

            snapshots = sorted(

                p

                for p in folder.iterdir()

                if p.is_dir()

            )

            return ReplaySession(

                snapshot_folders=snapshots

            )

        #
        # ------------------------------------------------------
        # Legacy Format
        #
        return ReplaySession(

            snapshot_folders=[folder]

        )