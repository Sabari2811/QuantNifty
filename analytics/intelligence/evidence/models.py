from __future__ import annotations

from dataclasses import dataclass, field

from analytics.intelligence.models import TradeIntelligenceRecord


@dataclass(slots=True)
class HistoricalEvidence:
    """
    Historical evidence produced after comparing the
    current market against historical memory.
    """

    #
    # Search Statistics
    #

    similar_markets: int = 0

    average_similarity: float = 0.0

    best_similarity: float = 0.0

    #
    # Trading Statistics
    #

    win_rate: float = 0.0

    average_pnl: float = 0.0

    average_holding_minutes: float = 0.0

    #
    # Exit Statistics
    #

    target_probability: float = 0.0

    stoploss_probability: float = 0.0

    breakeven_probability: float = 0.0

    #
    # Recommendation
    #

    recommendation: str = ""

    confidence_adjustment: float = 0.0

    confidence_after_validation: float = 0.0

    #
    # Explainability
    #

    explanation: str = ""

    #
    # Similar Markets
    #

    matches: list[TradeIntelligenceRecord] = field(
        default_factory=list
    )