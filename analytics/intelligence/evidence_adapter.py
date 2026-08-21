from __future__ import annotations

from typing import Any

from analytics.intelligence.result import EvidenceItem


class EvidenceAdapter:
    """
    Converts the authoritative AnalyticsPipeline result dictionary
    into normalized EvidenceItem objects.

    Input
    -----
    AnalyticsPipeline.run() result dictionary.

    Output
    ------
    tuple[EvidenceItem, ...]

    Responsibilities
    ----------------
    - Read existing analytics only.
    - Preserve directional semantics supplied by
      authoritative analytics engines.
    - Normalize them into EvidenceItem objects.

    This class MUST NOT:
    - calculate new indicators
    - modify analytics
    - create a new trading signal
    - make a BUY/SELL decision
    - execute trades
    """

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _mapping(value: Any) -> dict:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        if value is None:
            return default

        try:
            return float(value)

        except (TypeError, ValueError):
            return default

    @staticmethod
    def _direction_from_probability(
        bullish: float,
        bearish: float,
    ) -> str:

        if bullish > bearish:
            return "BULLISH"

        if bearish > bullish:
            return "BEARISH"

        return "NEUTRAL"

    @staticmethod
    def _direction_from_signal(
        signal: str,
    ) -> str:

        signal = str(signal or "").upper()

        if signal == "BUY CALL":
            return "BULLISH"

        if signal == "BUY PUT":
            return "BEARISH"

        return "NEUTRAL"

    @staticmethod
    def _direction_from_gamma_flip(
        direction: str,
    ) -> str:

        direction = str(direction or "").upper()

        if direction == "NEGATIVE_TO_POSITIVE":
            return "BULLISH"

        if direction == "POSITIVE_TO_NEGATIVE":
            return "BEARISH"

        return "NEUTRAL"

    @staticmethod
    def _append(
        items: list[EvidenceItem],
        *,
        source_family: str,
        feature: str,
        direction: str,
        strength: float,
        confidence: float,
        freshness: float = 100.0,
        independence: float = 1.0,
        reason: str = "",
    ) -> None:

        if direction == "NEUTRAL":
            return

        items.append(
            EvidenceItem(
                source_family=source_family,
                feature=feature,
                direction=direction,
                strength=strength,
                confidence=confidence,
                freshness=freshness,
                independence=independence,
                reason=reason,
            )
        )

    # ==========================================================
    # Main
    # ==========================================================

    def extract(
        self,
        analytics: dict | None,
    ) -> tuple[EvidenceItem, ...]:
        """
        Convert AnalyticsPipeline.run() output into EvidenceItems.

        Neutral and unavailable observations are omitted.
        """

        if not isinstance(analytics, dict):
            return ()

        items: list[EvidenceItem] = []

        # ======================================================
        # GAMMA FLIP
        # ======================================================

        gamma_flip = self._mapping(
            analytics.get("gamma_flip")
        )

        flip_direction = (
            self._direction_from_gamma_flip(
                gamma_flip.get("direction")
            )
        )

        if flip_direction != "NEUTRAL":

            self._append(
                items,
                source_family="GAMMA",
                feature="gamma_flip",
                direction=flip_direction,
                strength=100.0,
                confidence=100.0,
                reason=(
                    "Gamma flip direction: "
                    f"{gamma_flip.get('direction')}."
                ),
            )

        # ======================================================
        # DEALER GAMMA
        # ======================================================

        dealer = self._mapping(
            analytics.get("dealer")
        )

        dealer_gamma = str(
            dealer.get(
                "dealer_gamma",
                dealer.get(
                    "gamma",
                    "",
                ),
            )
            or ""
        ).upper()

        if dealer_gamma == "LONG":

            self._append(
                items,
                source_family="DEALER",
                feature="dealer_gamma",
                direction="BULLISH",
                strength=100.0,
                confidence=100.0,
                reason="Dealers are long gamma.",
            )

        elif dealer_gamma == "SHORT":

            self._append(
                items,
                source_family="DEALER",
                feature="dealer_gamma",
                direction="BEARISH",
                strength=100.0,
                confidence=100.0,
                reason="Dealers are short gamma.",
            )

        # ======================================================
        # OI FLOW
        # ======================================================

        oi_flow = self._mapping(
            analytics.get("oi_flow")
        )

        oi_summary = self._mapping(
            oi_flow.get("summary")
        )

        oi_bias = str(
            oi_summary.get(
                "market_bias",
                oi_flow.get(
                    "market_bias",
                    "",
                ),
            )
            or ""
        ).upper()

        if oi_bias in (
            "BULLISH",
            "BEARISH",
        ):

            self._append(
                items,
                source_family="OI_FLOW",
                feature="oi_flow_market_bias",
                direction=oi_bias,
                strength=100.0,
                confidence=100.0,
                reason=(
                    f"OI flow market bias: {oi_bias}."
                ),
            )

        # ======================================================
        # IV SKEW
        # ======================================================

        iv_skew = self._mapping(
            analytics.get("iv_skew")
        )

        iv_bias = str(
            iv_skew.get(
                "iv_bias",
                "",
            )
            or ""
        ).upper()

        if iv_bias == "CALLS_EXPENSIVE":

            self._append(
                items,
                source_family="VOLATILITY",
                feature="iv_skew",
                direction="BULLISH",
                strength=100.0,
                confidence=100.0,
                reason="Call IV is expensive.",
            )

        elif iv_bias == "PUTS_EXPENSIVE":

            self._append(
                items,
                source_family="VOLATILITY",
                feature="iv_skew",
                direction="BEARISH",
                strength=100.0,
                confidence=100.0,
                reason="Put IV is expensive.",
            )

        # ======================================================
        # PROBABILITY
        # ======================================================

        probability = self._mapping(
            analytics.get("probability")
        )

        bullish_probability = self._number(
            probability.get(
                "bullish_probability",
                0.0,
            )
        )

        bearish_probability = self._number(
            probability.get(
                "bearish_probability",
                0.0,
            )
        )

        probability_confidence = self._number(
            probability.get(
                "confidence",
                0.0,
            )
        )

        probability_direction = (
            self._direction_from_probability(
                bullish_probability,
                bearish_probability,
            )
        )

        if probability_direction != "NEUTRAL":

            probability_strength = max(
                bullish_probability,
                bearish_probability,
            )

            self._append(
                items,
                source_family="SCORE",
                feature="probability",
                direction=probability_direction,
                strength=probability_strength,
                confidence=probability_confidence,
                reason=(
                    "Bullish probability="
                    f"{bullish_probability:.1f}, "
                    "bearish probability="
                    f"{bearish_probability:.1f}."
                ),
            )

        # ======================================================
        # SIGNAL
        # ======================================================

        signal = self._mapping(
            analytics.get("signal")
        )

        signal_value = str(
            signal.get(
                "signal",
                "",
            )
            or ""
        ).upper()

        signal_confidence = self._number(
            signal.get(
                "confidence",
                probability_confidence,
            )
        )

        signal_direction = (
            self._direction_from_signal(
                signal_value
            )
        )

        if signal_direction != "NEUTRAL":

            self._append(
                items,
                source_family="SCORE",
                feature="signal",
                direction=signal_direction,
                strength=signal_confidence,
                confidence=signal_confidence,
                reason=(
                    f"Authoritative signal: "
                    f"{signal_value}."
                ),
            )

        # ======================================================
        # MARKET STRUCTURE
        # ======================================================

        structure = self._mapping(
            analytics.get("market_structure")
        )

        structure_direction = str(
            structure.get(
                "direction",
                "",
            )
            or ""
        ).upper()

        if structure_direction in (
            "BULLISH",
            "BEARISH",
        ):

            structure_strength = self._number(
                structure.get(
                    "strength",
                    100.0,
                ),
                100.0,
            )

            structure_confidence = self._number(
                structure.get(
                    "confidence",
                    100.0,
                ),
                100.0,
            )

            self._append(
                items,
                source_family="STRUCTURE",
                feature="market_structure",
                direction=structure_direction,
                strength=structure_strength,
                confidence=structure_confidence,
                reason=(
                    "Market structure: "
                    f"{structure_direction}."
                ),
            )

        return tuple(items)