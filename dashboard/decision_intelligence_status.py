from __future__ import annotations

from analytics.intelligence.decision_consistency import reconcile_decision_intelligence


def build_decision_intelligence_status(decision, intelligence):
    """Expose canonical Decision ↔ Intelligence semantics for UI rendering."""
    result = reconcile_decision_intelligence(decision, intelligence)
    return {
        "status": result.status,
        "semantic_status": result.semantic_status,
        "consistent": result.consistent,
        "actionable": result.actionable,
        "vetoed": result.vetoed,
        "decision_signal": result.decision_signal,
        "intelligence_recommendation": result.intelligence_recommendation,
        "intelligence_direction": result.intelligence_direction,
        "reason": result.reason,
    }
