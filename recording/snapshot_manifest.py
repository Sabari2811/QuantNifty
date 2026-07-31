from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(slots=True)
class SnapshotManifest:
    """
    Describes the contents of one snapshot folder.

    ReplayLoader will read ONLY this file to discover
    the snapshot contents.
    """

    # ======================================================
    # Metadata
    # ======================================================

    quantnifty_version: str = "1.0.0"

    recorder_version: str = "1.0.0"

    snapshot_version: str = "1.0.0"

    # ======================================================
    # Files
    # ======================================================

    runtime: str = "runtime.json"

    analytics: str = "analytics.json"

    decision: str = "decision.json"

    explanation: str = "explanation.json"

    option_chain: str = "option_chain.parquet"

    greeks: str = "greeks.parquet"

    # ======================================================
    # Save
    # ======================================================

    def save(self, folder: Path):

        with open(
            folder / "manifest.json",
            "w",
            encoding="utf-8"
        ) as fp:

            json.dump(
                asdict(self),
                fp,
                indent=4
            )

    # ======================================================
    # Load
    # ======================================================

    @classmethod
    def load(cls, folder: Path):

        with open(
            folder / "manifest.json",
            "r",
            encoding="utf-8"
        ) as fp:

            data = json.load(fp)

        return cls(**data)