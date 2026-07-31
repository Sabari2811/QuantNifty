from dataclasses import dataclass


@dataclass
class MarketRegime:

    regime: str = "UNKNOWN"

    trend: str = "NEUTRAL"

    volatility: str = "NORMAL"

    confidence: int = 0