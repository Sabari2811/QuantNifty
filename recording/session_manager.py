from __future__ import annotations

import json

from pathlib import Path
from datetime import datetime
from dataclasses import asdict

from recording.session_metadata import SessionMetadata


class SessionManager:
    """
    Manages one recording session.

    Responsibilities
    ----------------

    • Open today's session

    • Resume existing session

    • Allocate snapshot numbers

    • Persist metadata
    """

    def __init__(self, root="data/snapshots"):

        self.root = Path(root)

        self.metadata = None

        self.session_folder = None

    # =====================================================
    # Session
    # =====================================================

    def open(self):

        today = datetime.now().strftime("%d-%b-%Y")

        self.session_folder = self.root / today

        self.session_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        metadata_file = (

            self.session_folder

            / "session.json"

        )

        #
        # Resume
        #
        if metadata_file.exists():

            with open(

                metadata_file,

                "r",

                encoding="utf-8"

            ) as fp:

                data = json.load(fp)

            self.metadata = SessionMetadata(

                **data

            )

        #
        # New Session
        #
        else:

            self.metadata = SessionMetadata(

                session_id=today,

                started_at=datetime.now()

            )

            self.save()

        return self.metadata

    # =====================================================
    # Snapshot Number
    # =====================================================

    def next_snapshot_name(self, timestamp):

        if self.metadata is None:

            self.open()

        self.metadata.increment()

        self.metadata.last_snapshot = timestamp

        self.save()

        return (

            f"{self.metadata.snapshot_count:06d}"

            f"_{timestamp.replace(':','-')}"

        )

    # =====================================================
    # Save
    # =====================================================

    def save(self):

        if self.metadata is None:
            return

        data = asdict(self.metadata)

        #
        # Convert datetime objects to ISO strings
        #
        for key, value in data.items():

            if isinstance(value, datetime):

                data[key] = value.isoformat()

        with open(
            self.session_folder / "session.json",
            "w",
            encoding="utf-8"
        ) as fp:

            json.dump(
                data,
                fp,
                indent=4
            )