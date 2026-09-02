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
        return self.semantic_status == "CONSISTENT"

    @property
    def vetoed(self) -> bool:
        return not self.actionable


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
    """Return True when the exposed recommendation is historical evidence output.

    The current IntelligenceService assigns IntelligenceResult.recommendation
    from HistoricalEvidence.recommendation. That value is a historical
    validation recommendation, not a canonical final trade-actionability
    decision. It must not be interpreted as an execution veto merely because
    it is WAIT while the synthesized intelligence direction agrees with the
    authoritative Decision.

    A future final-actionability producer can be introduced explicitly without
    changing this direction contract.
    """
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

    The current ``IntelligenceResult.recommendation`` field is populated from
    ``HistoricalEvidence.recommendation`` by ``IntelligenceService``. Until a
    separate canonical final-actionability producer exists, that historical
    recommendation is diagnostic context and must not be used as an execution
    veto. Direction remains the authoritative synthesized Intelligence thesis.

    ``Decision.authoritative_signal`` is preferred over the mutable execution
    signal. Execution preparation may change ``signal.name`` to WAIT when a
    trade cannot be prepared or validated; that mutation must not erase the
    original Decision used for semantic reconciliation.
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

    # Historical validation is not final actionability. If the synthesized
    # direction agrees with the Decision, a historical WAIT must not create a
    # false deferred/vetoed state.
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
