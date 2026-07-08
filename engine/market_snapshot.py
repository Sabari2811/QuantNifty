from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketSnapshot:
    """
    Central market state shared across QuantNifty.
    """

    # Market
    symbol: str = "NIFTY"

    spot: float = 0.0

    future: float = 0.0

    expiry: str = ""

    timestamp: datetime = None

    # Volatility
    india_vix: float = 0.0

    # Session
    market_open: bool = True

    trading_day: str = ""

    def update(
        self,
        symbol,
        spot,
        expiry,
        future=0.0,
        india_vix=0.0
    ):

        self.symbol = symbol

        self.spot = spot

        self.future = future

        self.expiry = expiry

        self.india_vix = india_vix

        self.timestamp = datetime.now()

    def to_dict(self):

        return {

            "symbol": self.symbol,

            "spot": self.spot,

            "future": self.future,

            "expiry": self.expiry,

            "india_vix": self.india_vix,

            "timestamp": self.timestamp

        }