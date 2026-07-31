from dataclasses import dataclass, field

import pandas as pd


@dataclass
class MarketContext:
    """
    Internal Context Object

    Passed between all analytics engines.

    This object should NEVER be used directly
    by the UI.
    """

    # =====================================================
    # Market
    # =====================================================

    symbol: str = ""

    spot: float = 0.0

    expiry: str = ""

    # =====================================================
    # Raw Market Data
    # =====================================================

    option_chain: pd.DataFrame | None = None

    greeks: pd.DataFrame | None = None

    # =====================================================
    # Gamma Analytics
    # =====================================================

    gamma_flip: dict = field(default_factory=dict)

    gamma_wall: dict = field(default_factory=dict)

    # =====================================================
    # Dealer Analytics
    # =====================================================

    dealer: dict = field(default_factory=dict)

    # =====================================================
    # Open Interest
    # =====================================================

    oi_flow: dict = field(default_factory=dict)

    # =====================================================
    # IV Analytics
    # =====================================================

    iv_skew: dict = field(default_factory=dict)

    iv_smile: dict = field(default_factory=dict)

    # =====================================================
    # Volatility
    # =====================================================

    atr: dict = field(default_factory=dict)

    # =====================================================
    # Decision Engines
    # =====================================================

    probability: dict = field(default_factory=dict)

    signal: dict = field(default_factory=dict)

    trade_plan: dict = field(default_factory=dict)

    risk: dict = field(default_factory=dict)

    # =====================================================
    # Future Engines
    # =====================================================

    max_pain: dict = field(default_factory=dict)

    pcr: dict = field(default_factory=dict)

    oi_shift: dict = field(default_factory=dict)

    market_structure: dict = field(default_factory=dict)

    smart_strike: dict = field(default_factory=dict)