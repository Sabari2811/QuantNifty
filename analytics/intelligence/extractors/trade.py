from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class TradeExtractor(BaseExtractor):
    """
    Extracts trade information from TradingDecision.
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

        trade = getattr(
            decision,
            "trade",
            None,
        )

        if trade is None:
            return

        record.strike = getattr(
            trade,
            "strike",
            0.0,
        )

        record.option_type = getattr(
            trade,
            "option_type",
            "",
        )

        record.entry_price = getattr(
            trade,
            "entry",
            0.0,
        )

        record.stop_loss = getattr(
            trade,
            "stop_loss",
            0.0,
        )

        record.target1 = getattr(
            trade,
            "target1",
            0.0,
        )

        record.target2 = getattr(
            trade,
            "target2",
            0.0,
        )

        record.risk_reward = getattr(
            trade,
            "risk_reward",
            0.0,
        )

        execution = getattr(
            trade,
            "execution",
            None,
        )

        if execution is not None:

            record.quantity = (
                getattr(execution, "lot_size", 0)
                * getattr(execution, "lots", 0)
            )

            record.lots = getattr(
                execution,
                "lots",
                0,
            )