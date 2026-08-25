from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from core.data_provenance import RuntimeDataProvenance
from recording.snapshot_manifest import SnapshotManifest
from simulation.replay_snapshot import ReplaySnapshot


class ReplayLoader:
    """Loads a recorded snapshot from disk into a ReplaySnapshot."""

    def load(self, folder: str | Path) -> ReplaySnapshot:
        folder = Path(folder)
        manifest = SnapshotManifest.load(folder)
        snapshot = ReplaySnapshot()

        snapshot.runtime = self._load_json(folder / manifest.runtime)
        snapshot.analytics = self._load_json(folder / manifest.analytics)
        snapshot.decision = self._load_json(folder / manifest.decision)
        snapshot.explanation = self._load_json(folder / manifest.explanation)
        snapshot.intelligence = self._load_json(folder / manifest.intelligence)
        snapshot.option_chain = self._load_dataframe(folder / manifest.option_chain)
        snapshot.greeks = self._load_dataframe(folder / manifest.greeks)
        snapshot.data_provenance = RuntimeDataProvenance.from_dict(
            snapshot.runtime.get("data_provenance")
        )

        return snapshot

    def _load_json(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    def _load_dataframe(self, path: Path) -> pd.DataFrame:
        if not path.exists():
            return pd.DataFrame()
        return pd.read_parquet(path)
