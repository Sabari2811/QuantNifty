from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from models.dealer_data import DealerData


@dataclass
class DashboardData:

    # ======================================================
    # Basic
    # ======================================================

    provider: str
    symbol: str
    spot: float
    expiry: str

    # ======================================================
    # Dealer
    # ======================================================

    dealer: DealerData
    dealer_flow: dict

    # ======================================================
    # Institutional Analytics
    # ======================================================

    expected_move: dict
    max_pain: dict
    pcr: dict
    market_structure: dict
    liquidity: dict

    # ======================================================
    # Trading Analytics
    # ======================================================

    probability: dict
    signal: dict
    trade_plan: dict
    risk: dict
    institutional_score: dict

    # ======================================================
    # Raw Analytics
    # ======================================================

    analytics: dict

    # ======================================================
    # Market Data
    # ======================================================

    option_chain: pd.DataFrame
    greeks: pd.DataFrame

    # ======================================================
    # Runtime (Live Engine)
    # ======================================================

    portfolio: Any = None

    position: Any = None

    last_trade: Any = None

    journal: Any = None

    statistics: dict = field(default_factory=dict)

    risk_state: Any = None

    trade_status: str = ""

    trade_block_reason: str = ""

    runtime_status: str = ""

    cycle_no: int = 0