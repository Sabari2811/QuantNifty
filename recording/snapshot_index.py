from __future__ import annotations

from pathlib import Path
import csv


class SnapshotIndex:
    """
    Maintains a searchable index of all recorded snapshots.

    File:

        data/snapshots/index.csv
    """

    HEADER = [
        "timestamp",
        "date",
        "time",
        "symbol",
        "spot",
        "regime",
        "trade_status",
        "cycle_no",
        "folder"
    ]

    def __init__(self, root="data/snapshots"):

        self.root = Path(root)

        self.index_file = self.root / "index.csv"

        self._initialize()

    # ==========================================================
    # Initialization
    # ==========================================================

    def _initialize(self):

        self.root.mkdir(
            parents=True,
            exist_ok=True
        )

        if self.index_file.exists():
            return

        with open(
            self.index_file,
            "w",
            newline="",
            encoding="utf-8"
        ) as fp:

            writer = csv.writer(fp)

            writer.writerow(self.HEADER)

    # ==========================================================
    # Public
    # ==========================================================

    def append(self, ctx, folder):

        timestamp = getattr(ctx, "timestamp", "")

        date_part = ""
        time_part = ""

        if timestamp:

            date_part, time_part = timestamp.split()

        row = [

            timestamp,

            date_part,

            time_part,

            getattr(ctx, "symbol", ""),

            getattr(ctx, "spot", ""),

            getattr(ctx, "regime", ""),

            getattr(ctx, "trade_status", ""),

            getattr(ctx, "cycle_no", ""),

            str(folder)

        ]

        with open(
            self.index_file,
            "a",
            newline="",
            encoding="utf-8"
        ) as fp:

            writer = csv.writer(fp)

            writer.writerow(row)