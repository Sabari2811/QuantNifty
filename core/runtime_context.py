from dataclasses import dataclass, field
from typing import Any

from core.data_provenance import RuntimeDataProvenance
from models.market_context import MarketContext


@dataclass
class RuntimeContext:
    """
    Carries all runtime information through the QuantNifty runtime.

    Shared by LiveEngine, Analytics Pipeline, Decision Engine,
    Intelligence Layer, Paper Trading, and Dashboard.

    ``market_context`` is the typed canonical analytics artifact produced by
    ``AnalyticsPipeline``. ``analytics`` remains the serialized dictionary
    compatibility projection used by snapshots/replay and legacy consumers.
    """

    symbol: str = "NIFTY"
    strike_levels: int = 5
    spot: float = 0.0
    expiry: str = ""
    timestamp: str = ""

    option_chain: Any = None
    greeks_df: Any = None
    candles: Any = None

    data_provenance: RuntimeDataProvenance = field(
        default_factory=RuntimeDataProvenance
    )

    # Canonical typed analytics state. This is the runtime authority for
    # analytics produced by AnalyticsPipeline.
    market_context: MarketContext = field(default_factory=MarketContext)

    # Backward-compatible serialized analytics projection. Snapshot/replay
    # continues to persist this established dictionary contract.
    analytics: dict = field(default_factory=dict)

    # Replay recomputation diagnostics. The recomputed context is retained for
    # audit visibility, while the recorded analytics remain canonical for the
    # replay snapshot/UI surface when a recorded projection is available.
    replay_computed_market_context: Any = None
    replay_analytics_equivalence: Any = None
    replay_computed_analytics: Any = None

    features: dict = field(default_factory=dict)
    regime: Any = None

    snapshot: Any = None
    decision: Any = None
    explanation: Any = None
    intelligence: Any = None
    decision_intelligence_consistency: Any = None

    portfolio: Any = None
    position: Any = None
    last_trade: Any = None
    journal: Any = None
    performance: Any = None
    risk_state: Any = None
    trade_status: str = ""
    trade_block_reason: str = ""

    runtime_status: str = "READY"
    cycle_no: int = 0
