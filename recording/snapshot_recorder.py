from __future__ import annotations

import json
from pathlib import Path
from dataclasses import asdict, is_dataclass
from datetime import date, datetime

import pandas as pd

from recording.snapshot_index import SnapshotIndex
from recording.snapshot_manifest import SnapshotManifest


class SnapshotRecorder:
    """Records one complete QuantNifty market snapshot."""

    def __init__(self, root="data/snapshots"):
        self.root = Path(root)
        self.index = SnapshotIndex(root)
        self.manifest = SnapshotManifest()

    def save(self, ctx, folder=None):
        folder = self._snapshot_folder(ctx) if folder is None else Path(folder)
        intelligence = getattr(ctx, "intelligence", None)
        if intelligence is None or (
            isinstance(intelligence, dict) and not intelligence
        ):
            return False

        folder.mkdir(parents=True, exist_ok=True)

        self.manifest.save(folder)
        self._save_runtime(folder, ctx)
        self._save_json(folder / self.manifest.analytics, getattr(ctx, "analytics", None))
        self._save_json(folder / self.manifest.decision, getattr(ctx, "decision", None))
        self._save_json(folder / self.manifest.explanation, getattr(ctx, "explanation", None))
        self._save_json(folder / self.manifest.intelligence, intelligence)
        self._save_dataframe(folder / self.manifest.option_chain, getattr(ctx, "option_chain", None))
        self._save_dataframe(folder / self.manifest.greeks, getattr(ctx, "greeks_df", None))
        self.index.append(ctx, folder)
        return True

    def _snapshot_folder(self, ctx):
        timestamp = getattr(ctx, "timestamp", None)
        if timestamp is None:
            raise ValueError("RuntimeContext.timestamp is missing.")
        date_part, time_part = timestamp.split()
        cycle = getattr(ctx, "cycle_no", 0)
        folder_name = f"{cycle:06d}_{time_part.replace(':', '-')}"
        return self.root / date_part / folder_name

    def _save_runtime(self, folder, ctx):
        runtime = {
            "quantnifty_version": self.manifest.quantnifty_version,
            "recorder_version": self.manifest.recorder_version,
            "snapshot_version": self.manifest.snapshot_version,
            "timestamp": getattr(ctx, "timestamp", None),
            "cycle_no": getattr(ctx, "cycle_no", None),
            "symbol": getattr(ctx, "symbol", None),
            "spot": getattr(ctx, "spot", None),
            "expiry": str(getattr(ctx, "expiry", "")),
            "runtime_status": getattr(ctx, "runtime_status", None),
            "regime": getattr(ctx, "regime", None),
            "trade_status": getattr(ctx, "trade_status", None),
            "trade_block_reason": getattr(ctx, "trade_block_reason", None),
            "data_provenance": getattr(ctx, "data_provenance", None),
        }
        self._save_json(folder / self.manifest.runtime, runtime)

    @staticmethod
    def _json_default(value):
        if is_dataclass(value):
            return asdict(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return str(value)

    def _save_json(self, path, obj):
        if obj is None:
            return
        if is_dataclass(obj):
            obj = asdict(obj)
        with open(path, "w", encoding="utf-8") as fp:
            json.dump(obj, fp, indent=4, default=self._json_default)

    def _save_dataframe(self, path, df):
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            return
        serializable = df.copy(deep=False)
        serializable.attrs = json.loads(json.dumps(df.attrs, default=self._json_default))
        serializable.to_parquet(path, index=False)
