from types import SimpleNamespace

from analytics.intelligence.decision_consistency import (
    reconcile_decision_intelligence,
)


def decision(signal, authoritative_signal=""):
    return SimpleNamespace(
        signal=SimpleNamespace(name=signal),
        authoritative_signal=authoritative_signal,
    )


def intelligence(recommendation, direction=""):
    return SimpleNamespace(recommendation=recommendation, direction=direction)


def test_actionable_decision_conflicts_with_waiting_intelligence():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("WAIT", "BULLISH"),
    )

    assert result.status == "CONFLICT"
    assert result.consistent is False
    assert "BUY CALL" in result.reason
    assert "WAIT" in result.reason


def test_matching_actionable_direction_is_consistent():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("BUY CALL", "BULLISH"),
    )

    assert result.status == "CONSISTENT"
    assert result.consistent is True


def test_wait_decision_does_not_create_a_false_conflict():
    result = reconcile_decision_intelligence(
        decision("WAIT"),
        intelligence("WAIT", "NEUTRAL"),
    )

    assert result.status == "CONSISTENT"
    assert result.consistent is True


def test_authoritative_signal_survives_post_execution_wait_mutation():
    result = reconcile_decision_intelligence(
        decision("WAIT", authoritative_signal="BUY PUT"),
        intelligence("WAIT", "BULLISH"),
    )

    assert result.status == "CONFLICT"
    assert result.semantic_status == "CONFLICT"
    assert result.decision_signal == "BUY PUT"
    assert result.intelligence_direction == "BULLISH"
    assert result.actionable is False
    assert result.vetoed is True
