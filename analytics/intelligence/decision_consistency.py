from __future__ import annotations

from dataclasses import dataclass

from analytics.intelligence.evidence.models import HistoricalEvidence


@dataclass(frozen=True, slots=True)
class DecisionIntelligenceConsistency:
    """Deterministic reconciliation between canonical decision and intelligence."""

    status: str
    decision_signal: str
    intelligence_recommendation: str
    intelligence_direction: str
    reason: str
    semantic_status: str = "CONSISTENT"

    @property
    def consistent(self) -> bool:
        return self.status == "CONSISTENT"

    @property
    def actionable(self) -> bool:
        """Whether the reconciled state represents an actionable Decision."""
        return self.consistent and self.decision_signal not in {"", "WAIT"}

    @property
    def vetoed(self) -> bool:
        """Whether Intelligence prevents an otherwise actionable Decision."""
        return self.semantic_status in {"CONFLICT", "DEFERRED"}


def _decision_signal(decision) -> str:
    authoritative = str(getattr(decision, "authoritative_signal", "") or "").upper()
    if authoritative:
        return authoritative
    signal = getattr(getattr(decision, "signal", None), "name", "")
    return str(signal or "").upper()


def _recommendation(intelligence) -> str:
    return str(getattr(intelligence, "recommendation", "") or "").upper()


def _direction(intelligence) -> str:
    return str(getattr(intelligence, "direction", "") or "").upper()


def _recommendation_is_historical_validation(intelligence) -> bool:
    """Return True when the exposed recommendation is historical evidence output."""
    evidence = getattr(intelligence, "evidence", None)
    recommendation = _recommendation(intelligence)

    return (
        isinstance(evidence, HistoricalEvidence)
        and bool(recommendation)
        and str(getattr(evidence, "recommendation", "") or "").upper()
        == recommendation
    )


def reconcile_decision_intelligence(decision, intelligence) -> DecisionIntelligenceConsistency:
    """Reconcile authoritative Decision direction with Intelligence semantics.

    Consistency, actionability, and veto state are intentionally separate:
    WAIT is a valid consistent non-actionable state, while CONFLICT/DEFERRED
    indicate that Intelligence prevents an otherwise actionable Decision.
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
            semantic_status="CONFLICT",
        )

    if _recommendation_is_historical_validation(intelligence):
        return DecisionIntelligenceConsistency(
            status="CONSISTENT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason=(
                "Intelligence direction agrees with the Decision; "
                "historical validation recommendation is diagnostic and "
                "does not veto execution."
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
            status="CONFLICT",
            decision_signal=signal,
            intelligence_recommendation=recommendation,
            intelligence_direction=direction,
            reason=(
                "Intelligence supports the Decision direction but defers execution: "
                f"decision={signal}, intelligence={recommendation or 'UNAVAILABLE'}."
            ),
            semantic_status="DEFERRED",
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
        semantic_status="CONFLICT",
    )
