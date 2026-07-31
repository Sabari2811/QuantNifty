from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketSnapshot:

    timestamp: datetime

    spot: float

    atm_strike: float

    volatility: str

    dealer_gamma: str

    regime: str

    pcr: float

    institutional_score: int