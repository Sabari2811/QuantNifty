from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class DecisionExtractor(BaseExtractor):
    """
    Extracts TradingDecision information.
    """

    def extract(
        self,
        ctx,
        record,
    ):

        decision = getattr(
            ctx,
            "decision",
            None,
        )

        if decision is None:
            return

        signal = getattr(
            decision,
            "signal",
            None,
        )

        if signal is not None:

            record.signal = getattr(
                signal,
                "name",
                "",
            )

        record.confidence = getattr(
            decision,
            "confidence",
            0.0,
        )

        record.trade_quality = getattr(
            decision,
            "trade_quality",
            0.0,
        )

        record.strategy_name = getattr(
            decision,
            "strategy_name",
            "",
        )

        record.execution_plan = getattr(
            decision,
            "execution_plan",
            "",
        )

        record.reasons = list(
            getattr(
                decision,
                "reasons",
                [],
            )
        )