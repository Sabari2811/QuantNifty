from dataclasses import dataclass


@dataclass(slots=True)
class HistoricalValidation:

    similar_markets: int = 0

    average_similarity: float = 0.0

    win_rate: float = 0.0

    average_pnl: float = 0.0

    average_holding_minutes: float = 0.0

    target1_probability: float = 0.0

    stoploss_probability: float = 0.0

    recommendation: str = ""

    confidence_adjustment: float = 0.0