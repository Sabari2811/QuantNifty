from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecisionIntelligenceConsistency:
    """Deterministic reconciliation between canonical decision and intelligence."""

    status: str
    decision_signal: str
    intelligence_recommendation: str
    reason: str

    @property
    def consistent(self) -> bool:
        return self.status == "CONSISTENT"


def _decision_signal(decision) -> str:
    signal = getattr(getattr(decision, "signal", None), "name", "")
    return str(signal or "").upper()


def _recommendation(intelligence) -> str:
    return str(getattr(intelligence, "recommendation", "") or "").upper()


def reconcile_decision_intelligence(decision, intelligence) -> DecisionIntelligenceConsistency:
    """Reconcile actionable Decision direction with Intelligence recommendation.

    WAIT/NO_TRADE intelligence is treated as a safety veto when the canonical
    decision requests an actionable BUY CALL or BUY PUT. The two objects are
    allowed to differ directionally only when the Intelligence layer explicitly
    recommends the same actionable direction or the canonical decision is WAIT.
    """
    signal = _decision_signal(decision)
    recommendation = _recommendation(intelligence)

    if signal in {"", "WAIT"}:
        return DecisionIntelligenceConsistency(
            status="CONSISTENT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            reason="Decision is non-actionable; Intelligence does not veto it.",
        )

    if signal == "BUY CALL":
        expected = {"BUY CALL", "BUY"}
    elif signal == "BUY PUT":
        expected = {"BUY PUT", "SELL", "SELL PUT"}
    else:
        expected = {signal}

    if recommendation in expected:
        return DecisionIntelligenceConsistency(
            status="CONSISTENT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            reason="Decision and Intelligence agree on the actionable direction.",
        )

    return DecisionIntelligenceConsistency(
        status="CONFLICT",
        decision_signal=signal,
        intelligence_recommendation=recommendation,
        reason=(
            "Intelligence does not endorse the actionable Decision: "
            f"decision={signal}, intelligence={recommendation or 'UNAVAILABLE'}."
        ),
    )
