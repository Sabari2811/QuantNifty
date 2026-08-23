from dataclasses import dataclass, field
from typing import Any

from core.data_provenance import RuntimeDataProvenance


@dataclass
class RuntimeContext:
    """
    Carries all runtime information
    through the QuantNifty runtime.

    Shared by

        LiveEngine
            ↓
        Analytics Pipeline
            ↓
        Decision Engine
            ↓
        Intelligence Layer
            ↓
        Paper Trading
            ↓
        Dashboard
    """

    # ==========================================================
    # MARKET
    # ==========================================================

    symbol: str = "NIFTY"

    spot: float = 0.0

    expiry: str = ""

    timestamp: str = ""

    # ==========================================================
    # RAW MARKET DATA
    # ==========================================================

    option_chain: Any = None

    greeks_df: Any = None

    candles: Any = None

    # ==========================================================
    # DATA PROVENANCE
    # ==========================================================

    data_provenance: RuntimeDataProvenance = field(
        default_factory=RuntimeDataProvenance
    )

    # ==========================================================
    # ANALYTICS
    # ==========================================================

    analytics: dict = field(default_factory=dict)

    features: dict = field(default_factory=dict)

    regime: Any = None

    # ==========================================================
    # DOMAIN OBJECTS
    # ==========================================================

    snapshot: Any = None

    decision: Any = None

    explanation: Any = None

    intelligence: Any = None

    # ==========================================================
    # PAPER TRADING
    # ==========================================================

    portfolio: Any = None

    position: Any = None

    last_trade: Any = None

    journal: Any = None

    performance: Any = None

    # Risk Manager State

    risk_state: Any = None

    trade_status: str = ""

    trade_block_reason: str = ""

    # ==========================================================
    # RUNTIME
    # ==========================================================

    runtime_status: str = "READY"

    cycle_no: int = 0
