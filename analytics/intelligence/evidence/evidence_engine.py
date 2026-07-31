from __future__ import annotations

from analytics.intelligence.evidence.models import HistoricalEvidence
from analytics.intelligence.memory_engine import MarketMemory
from analytics.intelligence.models import TradeIntelligenceRecord
from analytics.intelligence.similarity.similarity_engine import SimilarityEngine


class EvidenceEngine:
    """
    Converts historical market memory into actionable evidence.

    Responsibilities
    ----------------
    - Search historical memory
    - Aggregate historical statistics
    - Produce explainable evidence

    Notes
    -----
    This class owns NO dependencies.
    All dependencies are injected.
    """

    def __init__(
        self,
        similarity_engine: SimilarityEngine,
    ):

        self._similarity_engine = similarity_engine

    def analyze(
        self,
        current: TradeIntelligenceRecord,
        memory: MarketMemory,
    ) -> HistoricalEvidence:

        evidence = HistoricalEvidence()

        matches = self._similarity_engine.search(
            current=current,
            history=memory.records,
            top_n=100,
        )

        if not matches:
            return evidence

        scores = [score for score, _ in matches]
        records = [record for _, record in matches]

        evidence.matches = records
        evidence.similar_markets = len(records)
        evidence.average_similarity = sum(scores) / len(scores)
        evidence.best_similarity = max(scores)

        wins = [
            record
            for record in records
            if record.outcome == "WIN"
        ]

        losses = [
            record
            for record in records
            if record.outcome == "LOSS"
        ]

        breakevens = [
            record
            for record in records
            if record.outcome == "BREAKEVEN"
        ]

        evidence.win_rate = (
            len(wins) / len(records)
        ) * 100

        evidence.average_pnl = (
            sum(r.pnl for r in records)
            / len(records)
        )

        evidence.average_holding_minutes = (
            sum(r.holding_minutes for r in records)
            / len(records)
        )

        evidence.target_probability = (
            len(wins)
            / len(records)
        ) * 100

        evidence.stoploss_probability = (
            len(losses)
            / len(records)
        ) * 100

        evidence.breakeven_probability = (
            len(breakevens)
            / len(records)
        ) * 100

        #
        # Confidence Adjustment
        #

        if evidence.win_rate >= 70:

            evidence.recommendation = "BUY"
            evidence.confidence_adjustment = 5.0

        elif evidence.win_rate >= 55:

            evidence.recommendation = "BUY"
            evidence.confidence_adjustment = 2.0

        elif evidence.win_rate >= 45:

            evidence.recommendation = "WAIT"
            evidence.confidence_adjustment = 0.0

        else:

            evidence.recommendation = "WAIT"
            evidence.confidence_adjustment = -5.0

        evidence.confidence_after_validation = (
            evidence.confidence_adjustment
        )

        evidence.explanation = (
            f"Found {evidence.similar_markets} similar historical "
            f"markets with {evidence.win_rate:.1f}% win rate."
        )

        return evidence