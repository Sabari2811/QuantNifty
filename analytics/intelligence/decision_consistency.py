from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecisionIntelligenceConsistency:
    """Deterministic reconciliation between canonical decision and intelligence."""

    status: str
    decision_signal: str
    intelligence_recommendation: str
    intelligence_direction: str
    reason: str

    @property
    def consistent(self) -> bool:
        return self.status in {"CONSISTENT", "DEFERRED"}

    @property
    def actionable(self) -> bool:
        return self.status == "CONSISTENT"

    @property
    def vetoed(self) -> bool:
        return self.status != "CONSISTENT"


def _decision_signal(decision) -> str:
    signal = getattr(getattr(decision, "signal", None), "name", "")
    return str(signal or "").upper()


def _recommendation(intelligence) -> str:
    return str(getattr(intelligence, "recommendation", "") or "").upper()


def _direction(intelligence) -> str:
    return str(getattr(intelligence, "direction", "") or "").upper()


def reconcile_decision_intelligence(decision, intelligence) -> DecisionIntelligenceConsistency:
    """Reconcile decision actionability with Intelligence thesis and recommendation.

    ``direction`` describes the Intelligence market thesis, while
    ``recommendation`` describes whether Intelligence endorses taking an action.
    Therefore ``BUY CALL`` + ``BULLISH/WAIT`` is not a directional conflict;
    it is a valid bullish thesis with an execution deferral.  Only an explicit
    opposite directional recommendation is classified as a conflict.
    """
    signal = _decision_signal(decision)
    recommendation = _recommendation(intelligence)
    direction = _direction(intelligence)

    if signal in {"", "WAIT"}:
        return DecisionIntelligenceConsistency(
            status="CONSISTENT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason="Decision is non-actionable; Intelligence does not veto it.",
        )

    if signal == "BUY CALL":
        expected_direction = "BULLISH"
        expected_recommendations = {"BUY CALL", "BUY"}
    elif signal == "BUY PUT":
        expected_direction = "BEARISH"
        expected_recommendations = {"BUY PUT", "SELL", "SELL PUT"}
    else:
        expected_direction = ""
        expected_recommendations = {signal}

    if direction and direction != expected_direction:
        return DecisionIntelligenceConsistency(
            status="CONFLICT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason=(
                "Intelligence direction conflicts with the actionable Decision: "
                f"decision={signal}, intelligence_direction={direction}."
            ),
        )

    if recommendation in expected_recommendations:
        return DecisionIntelligenceConsistency(
            status="CONSISTENT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason="Decision and Intelligence agree on direction and actionability.",
        )

    if recommendation in {"", "WAIT", "NO_TRADE", "NO TRADE", "HOLD"}:
        return DecisionIntelligenceConsistency(
            status="DEFERRED",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason=(
                "Intelligence supports the Decision direction but does not endorse "
                f"execution: decision={signal}, intelligence={recommendation or 'UNAVAILABLE'}."
            ),
        )

    return DecisionIntelligenceConsistency(
        status="CONFLICT",
        decision_signal=signal,
        intelligence_recommendation=recommendation,
        intelligence_direction=direction,
        reason=(
            "Intelligence does not endorse the actionable Decision: "
            f"decision={signal}, intelligence={recommendation or 'UNAVAILABLE'}."
        ),
    )
