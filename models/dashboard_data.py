from dataclasses import dataclass, field
from typing import Any

import pandas as pd

from models.dealer_data import DealerData
from core.data_provenance import RuntimeDataProvenance


@dataclass
class DashboardData:
    provider: str
    symbol: str
    spot: float
    expiry: str

    dealer: DealerData
    dealer_flow: dict

    expected_move: dict
    max_pain: dict
    pcr: dict
    market_structure: dict
    liquidity: dict

    probability: dict
    signal: dict
    trade_plan: dict
    risk: dict
    institutional_score: dict

    analytics: dict

    option_chain: pd.DataFrame
    greeks: pd.DataFrame
    data_provenance: RuntimeDataProvenance = field(default_factory=RuntimeDataProvenance)
    option_chain_integrity: dict | None = None

    intelligence: dict | None = None

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
