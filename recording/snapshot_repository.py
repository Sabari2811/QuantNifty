from __future__ import annotations

import json
from pathlib import Path

from recording.replay_recording import ReplayRecording


class SnapshotRepository:
    """
    Repository for recorded QuantNifty replay sessions.

    Each trading day is represented by one session folder
    containing:

        session.json
        000001_...
        000002_...
        ...
    """

    def __init__(self, root="data/snapshots"):

        self.root = Path(root)

    # =====================================================
    # PUBLIC
    # =====================================================

    def list_recordings(self) -> list[ReplayRecording]:

        recordings = []

        if not self.root.exists():
            return recordings

        #
        # Every date folder represents one replay session
        #
        for date_folder in sorted(
            self.root.iterdir(),
            reverse=True
        ):

            if not date_folder.is_dir():
                continue

            #
            # Only session-based recordings are supported
            #
            session_json = date_folder / "session.json"

            if not session_json.exists():
                continue

            recordings.append(
                self._build_session_recording(
                    date_folder
                )
            )

        return recordings

    # =====================================================
    # SESSION RECORDING
    # =====================================================

    def _build_session_recording(

        self,

        folder: Path

    ) -> ReplayRecording:

        snapshots = sorted(

            p

            for p in folder.iterdir()

            if p.is_dir()

        )

        timestamp = ""

        cycle = 0

        #
        # Use latest snapshot runtime
        #
        if snapshots:

            runtime_file = (

                snapshots[-1]

                / "runtime.json"

            )

            if runtime_file.exists():

                with open(

                    runtime_file,

                    encoding="utf-8"

                ) as fp:

                    runtime = json.load(fp)

                timestamp = runtime.get(

                    "timestamp",

                    ""

                )

                cycle = runtime.get(

                    "cycle_no",

                    0

                )

        return ReplayRecording(

            date=folder.name,

            session_name=folder.name,

            folder=folder,

            timestamp=timestamp,

            cycle=cycle,

            runtime=True,

            analytics=True,

            decision=True,

            explanation=True,

            greeks=True,

            option_chain=True,

            manifest=True

        )
