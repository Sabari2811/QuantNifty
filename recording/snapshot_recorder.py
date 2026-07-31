from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from recording.snapshot_index import SnapshotIndex
from recording.snapshot_manifest import SnapshotManifest


class SnapshotRecorder:
    """
    Records one complete QuantNifty market snapshot.

    Folder Structure
    ----------------

    data/
        snapshots/
            index.csv

            27-Jul-2026/
                000001_09-15-00/
                    manifest.json
                    runtime.json
                    analytics.json
                    decision.json
                    explanation.json
                    option_chain.parquet
                    greeks.parquet
    """

    def __init__(self, root="data/snapshots"):

        self.root = Path(root)

        self.index = SnapshotIndex(root)

        self.manifest = SnapshotManifest()

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def save(self, ctx):

        folder = self._snapshot_folder(ctx)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        #
        # Manifest
        #
        self.manifest.save(folder)

        #
        # Runtime
        #
        self._save_runtime(folder, ctx)

        #
        # Analytics
        #
        self._save_json(
            folder / self.manifest.analytics,
            getattr(ctx, "analytics", None)
        )

        #
        # Decision
        #
        self._save_json(
            folder / self.manifest.decision,
            getattr(ctx, "decision", None)
        )

        #
        # Explanation
        #
        self._save_json(
            folder / self.manifest.explanation,
            getattr(ctx, "explanation", None)
        )

        #
        # Option Chain
        #
        self._save_dataframe(
            folder / self.manifest.option_chain,
            getattr(ctx, "option_chain", None)
        )

        #
        # Greeks
        #
        self._save_dataframe(
            folder / self.manifest.greeks,
            getattr(ctx, "greeks_df", None)
        )

        #
        # Index
        #
        self.index.append(
            ctx,
            folder
        )

    # ==========================================================
    # PRIVATE
    # ==========================================================

    def _snapshot_folder(self, ctx):

        timestamp = getattr(ctx, "timestamp", None)

        if timestamp is None:
            raise ValueError(
                "RuntimeContext.timestamp is missing."
            )

        date_part, time_part = timestamp.split()

        cycle = getattr(ctx, "cycle_no", 0)

        folder_name = f"{cycle:06d}_{time_part.replace(':', '-')}"

        return (
            self.root
            / date_part
            / folder_name
        )

    def _save_runtime(self, folder, ctx):

        runtime = {

            "quantnifty_version":
                self.manifest.quantnifty_version,

            "recorder_version":
                self.manifest.recorder_version,

            "snapshot_version":
                self.manifest.snapshot_version,

            "timestamp":
                getattr(ctx, "timestamp", None),

            "cycle_no":
                getattr(ctx, "cycle_no", None),

            "symbol":
                getattr(ctx, "symbol", None),

            "spot":
                getattr(ctx, "spot", None),

            "expiry":
                str(getattr(ctx, "expiry", "")),

            "runtime_status":
                getattr(ctx, "runtime_status", None),

            "regime":
                getattr(ctx, "regime", None),

            "trade_status":
                getattr(ctx, "trade_status", None),

            "trade_block_reason":
                getattr(ctx, "trade_block_reason", None)
        }

        self._save_json(
            folder / self.manifest.runtime,
            runtime
        )

    def _save_json(self, path, obj):

        if obj is None:
            return

        #
        # Dataclass
        #
        if hasattr(obj, "__dict__"):
            obj = obj.__dict__

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as fp:

            json.dump(
                obj,
                fp,
                indent=4,
                default=str
            )

    def _save_dataframe(self, path, df):

        if df is None:
            return

        if not isinstance(df, pd.DataFrame):
            return

        if df.empty:
            return

        df.to_parquet(
            path,
            index=False
        )