from __future__ import annotations

import json
from pathlib import Path

from recording.replay_recording import ReplayRecording


class SnapshotRepository:
    """
    Repository for recorded QuantNifty snapshots.

    Responsibilities
    ----------------
    • Discover recordings
    • Read metadata
    • Build ReplayRecording objects

    Never loads analytics.
    Never loads option chain.
    Never loads greeks.
    """

    def __init__(self, root="data/snapshots"):

        self.root = Path(root)

    # =====================================================
    # Public
    # =====================================================

    def list_recordings(self) -> list[ReplayRecording]:

        recordings = []

        if not self.root.exists():
            return recordings

        #
        # Every folder = Trading Date
        #

        for date_folder in sorted(self.root.iterdir(), reverse=True):

            if not date_folder.is_dir():
                continue

            for session_folder in sorted(date_folder.iterdir()):

                if not session_folder.is_dir():
                    continue

                recordings.append(

                    self._build_recording(

                        date_folder.name,

                        session_folder

                    )

                )

        return recordings

    # =====================================================
    # Private
    # =====================================================

    def _build_recording(

        self,

        date,

        folder

    ) -> ReplayRecording:

        runtime_file = folder / "runtime.json"

        timestamp = ""

        cycle = 0

        if runtime_file.exists():

            with open(runtime_file, encoding="utf-8") as fp:

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

            date=date,

            session_name=folder.name,

            folder=folder,

            timestamp=timestamp,

            cycle=cycle,

            runtime=runtime_file.exists(),

            analytics=(folder / "analytics.json").exists(),

            decision=(folder / "decision.json").exists(),

            explanation=(folder / "explanation.json").exists(),

            greeks=(folder / "greeks.parquet").exists(),

            option_chain=(folder / "option_chain.parquet").exists(),

            manifest=(folder / "manifest.json").exists()

        )