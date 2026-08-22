from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class DecisionExtractor(BaseExtractor):
    """
    Extracts authoritative TradingDecision information.

    Source ownership
    ----------------
    signal:
        decision.signal.name

    confidence:
        decision.signal.confidence

    trade_quality:
        decision.trade.execution.trade_quality

    reasons:
        decision.reasons

    strategy_name:
        Not currently persisted on Decision.

    execution_plan:
        Not currently represented as a string field on Decision.
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

        # ======================================================
        # Signal
        # ======================================================

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
                signal,
                "confidence",
                0.0,
            )

        # ======================================================
        # Trade Quality
        # ======================================================

        trade = getattr(
            decision,
            "trade",
            None,
        )

        if trade is not None:

            execution = getattr(
                trade,
                "execution",
                None,
            )

            if execution is not None:

                record.trade_quality = getattr(
                    execution,
                    "trade_quality",
                    0.0,
                )

        # ======================================================
        # Strategy / Execution Plan
        # ======================================================
        #
        # Do NOT invent these values.
        #
        # The current Decision contract does not persist an
        # authoritative strategy name, and execution_plan is
        # represented by the trade execution object rather
        # than a string field on Decision.
        #
        # Leave the intelligence record at its default value
        # until ownership is explicitly added to the contract.

        # ======================================================
        # Reasons
        # ======================================================

        record.reasons = list(
            getattr(
                decision,
                "reasons",
                [],
            )
        )