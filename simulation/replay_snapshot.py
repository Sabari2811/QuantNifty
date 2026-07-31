from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class ReplaySnapshot:
    """
    Represents ONE recorded market cycle.

    This object is the bridge between:

        SnapshotRecorder

            ↓

        ReplayLoader

            ↓

        SimulationProvider

            ↓

        LiveEngine
    """

    # ======================================================
    # Metadata
    # ======================================================

    runtime: dict = field(default_factory=dict)

    analytics: dict = field(default_factory=dict)

    decision: dict = field(default_factory=dict)

    explanation: dict = field(default_factory=dict)

    # ======================================================
    # DataFrames
    # ======================================================

    option_chain: pd.DataFrame = field(
        default_factory=pd.DataFrame
    )

    greeks: pd.DataFrame = field(
        default_factory=pd.DataFrame
    )

    # ======================================================
    # Convenience Properties
    # ======================================================

    @property
    def timestamp(self):

        return self.runtime.get("timestamp")

    @property
    def spot(self):

        return self.runtime.get("spot")

    @property
    def symbol(self):

        return self.runtime.get("symbol")

    @property
    def regime(self):

        return self.runtime.get("regime")

    @property
    def trade_status(self):

        return self.runtime.get(
            "trade_status"
        )

    @property
    def cycle_no(self):

        return self.runtime.get(
            "cycle_no"
        )