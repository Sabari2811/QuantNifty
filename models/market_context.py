from dataclasses import dataclass, field

import pandas as pd


@dataclass
class MarketContext:
    """
    Internal canonical analytics context.

    Passed between analytics/runtime components. This object should NEVER
    be used directly by the UI; dashboard consumers must use DashboardData
    and its canonical adapters.

    The declared fields intentionally mirror the analytics result surface
    produced by AnalyticsPipeline.run(). Keeping the surface typed prevents
    silent drift through dynamically attached attributes.
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
    # Dealer / Exposure Analytics
    # =====================================================

    dealer: dict = field(default_factory=dict)
    dealer_flow: dict = field(default_factory=dict)
    liquidity: dict = field(default_factory=dict)

    # =====================================================
    # Open Interest
    # =====================================================

    oi_flow: dict = field(default_factory=dict)

    # =====================================================
    # IV / Expected Move
    # =====================================================

    iv_skew: dict = field(default_factory=dict)
    iv_smile: dict = field(default_factory=dict)
    expected_move: dict = field(default_factory=dict)

    # =====================================================
    # Volatility / Structure / Technical Analytics
    # =====================================================

    atr: dict = field(default_factory=dict)
    volatility: dict = field(default_factory=dict)
    market_structure: dict = field(default_factory=dict)
    technical: dict = field(default_factory=dict)

    # =====================================================
    # Derived Market Statistics
    # =====================================================

    max_pain: dict = field(default_factory=dict)
    pcr: dict = field(default_factory=dict)

    oi_shift: dict = field(default_factory=dict)

    # =====================================================
    # Decision Engines
    # =====================================================

    probability: dict = field(default_factory=dict)
    signal: dict = field(default_factory=dict)
    institutional_score: dict = field(default_factory=dict)
    smart_strike: dict = field(default_factory=dict)
    trade_plan: dict = field(default_factory=dict)
    risk: dict = field(default_factory=dict)

    # =====================================================
    # Canonical Market Map
    # =====================================================

    market_map: dict = field(default_factory=dict)

    @classmethod
    def from_analytics(cls, analytics, *, spot=0.0, greeks=None):
        """Reconstruct the typed canonical context from a serialized surface.

        Only declared analytics fields are restored. Snapshot identity values
        remain explicit inputs so replay cannot fabricate them from a legacy
        or incomplete analytics artifact.
        """
        context = cls(spot=spot, greeks=greeks)
        if not isinstance(analytics, dict):
            return context

        for field_name in (
            "dealer",
            "dealer_flow",
            "liquidity",
            "gamma_flip",
            "gamma_wall",
            "oi_flow",
            "iv_skew",
            "iv_smile",
            "expected_move",
            "max_pain",
            "pcr",
            "market_structure",
            "atr",
            "volatility",
            "technical",
            "oi_shift",
            "probability",
            "signal",
            "smart_strike",
            "trade_plan",
            "risk",
            "institutional_score",
            "market_map",
        ):
            if field_name in analytics:
                setattr(context, field_name, analytics[field_name])
        return context
