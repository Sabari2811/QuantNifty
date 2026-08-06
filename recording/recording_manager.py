from __future__ import annotations

from pathlib import Path

from recording.session_manager import SessionManager
from recording.snapshot_recorder import SnapshotRecorder


class RecordingManager:
    """
    Coordinates recording of market snapshots.

    Responsibilities
    ----------------

    • Maintain active recording session

    • Allocate snapshot folders

    • Delegate snapshot persistence

    LiveEngine talks ONLY to this class.
    """

    def __init__(self):

        self.session = SessionManager()

        self.recorder = SnapshotRecorder()

        self.session.open()

    # =====================================================
    # Record Snapshot
    # =====================================================

    def record(self, ctx):

        timestamp = ctx.timestamp.split()[1]

        folder_name = self.session.next_snapshot_name(
            timestamp
        )

        session_folder = (
            Path("data/snapshots")
            / self.session.metadata.session_id
            / folder_name
        )

        self.recorder.save(
            ctx,
            session_folder
        )