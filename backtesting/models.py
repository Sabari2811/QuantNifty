from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketCandle:
    """
    Generic market candle.

    Used for:
    - Historical replay
    - Live feeds
    - Paper trading
    """

    timestamp: datetime

    open: float

    high: float

    low: float

    close: float

    volume: int

    symbol: str = "NIFTY"

    timeframe: str = "5m"