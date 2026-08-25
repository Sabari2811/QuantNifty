from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from core.data_provenance import RuntimeDataProvenance


@dataclass(slots=True)
class ReplaySnapshot:
    """Represents ONE recorded market cycle."""

    runtime: dict = field(default_factory=dict)
    analytics: dict = field(default_factory=dict)
    decision: dict = field(default_factory=dict)
    explanation: dict = field(default_factory=dict)
    intelligence: dict = field(default_factory=dict)
    data_provenance: RuntimeDataProvenance = field(default_factory=RuntimeDataProvenance)

    option_chain: pd.DataFrame = field(default_factory=pd.DataFrame)
    greeks: pd.DataFrame = field(default_factory=pd.DataFrame)

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
        return self.runtime.get("trade_status")

    @property
    def cycle_no(self):
        return self.runtime.get("cycle_no")
