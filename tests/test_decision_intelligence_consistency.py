from types import SimpleNamespace

from analytics.intelligence.decision_consistency import (
    reconcile_decision_intelligence,
)


def decision(signal):
    return SimpleNamespace(signal=SimpleNamespace(name=signal))


def intelligence(recommendation):
    return SimpleNamespace(recommendation=recommendation)


def test_actionable_decision_conflicts_with_waiting_intelligence():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("WAIT"),
    )

    assert result.status == "CONFLICT"
    assert result.consistent is False
    assert "BUY CALL" in result.reason
    assert "WAIT" in result.reason


def test_matching_actionable_direction_is_consistent():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("BUY CALL"),
    )

    assert result.status == "CONSISTENT"
    assert result.consistent is True


def test_wait_decision_does_not_create_a_false_conflict():
    result = reconcile_decision_intelligence(
        decision("WAIT"),
        intelligence("WAIT"),
    )

    assert result.status == "CONSISTENT"
    assert result.consistent is True
