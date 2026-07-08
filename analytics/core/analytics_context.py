from dataclasses import dataclass, field
import pandas as pd

from engine.market_snapshot import MarketSnapshot


@dataclass
class AnalyticsContext:
    """
    Shared Analytics Context
    Passed between all QuantNifty engines.
    """

    # -----------------------------
    # Market Snapshot
    # -----------------------------

    snapshot: MarketSnapshot = field(
        default_factory=MarketSnapshot
    )

    # -----------------------------
    # Raw Data
    # -----------------------------

    option_chain: list = field(default_factory=list)

    greeks_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    # -----------------------------
    # Gamma
    # -----------------------------

    gamma_flip: dict = field(default_factory=dict)

    gamma_wall: dict = field(default_factory=dict)

    total_gex: float = 0

    total_dex: float = 0

    # -----------------------------
    # Open Interest
    # -----------------------------

    oi_flow: dict = field(default_factory=dict)

    # -----------------------------
    # IV
    # -----------------------------

    iv: dict = field(default_factory=dict)

    # -----------------------------
    # Dealer
    # -----------------------------

    dealer: dict = field(default_factory=dict)

    # -----------------------------
    # Probability
    # -----------------------------

    probability: dict = field(default_factory=dict)

    # -----------------------------
    # Signal
    # -----------------------------

    signal: dict = field(default_factory=dict)

    # -----------------------------
    # Strategy
    # -----------------------------

    strategy: dict = field(default_factory=dict)

    commentary: str = ""