from types import SimpleNamespace

from analytics.intelligence.decision_consistency import reconcile_decision_intelligence


def decision(signal):
    return SimpleNamespace(signal=SimpleNamespace(name=signal))


def intelligence(recommendation, direction):
    return SimpleNamespace(recommendation=recommendation, direction=direction)


def test_bullish_wait_is_deferred_not_opposite_direction():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("WAIT", "BULLISH"),
    )
    assert result.status == "CONFLICT"  # compatibility status: actionable decision is vetoed
    assert result.semantic_status == "DEFERRED"
    assert result.consistent is False
    assert result.actionable is False
    assert result.vetoed is True
    assert "defers execution" in result.reason


def test_opposite_direction_is_a_true_conflict():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("WAIT", "BEARISH"),
    )
    assert result.status == "CONFLICT"
    assert result.semantic_status == "CONFLICT"
    assert result.actionable is False
    assert "conflicts" in result.reason


def test_matching_actionable_recommendation_is_executable():
    result = reconcile_decision_intelligence(
        decision("BUY CALL"),
        intelligence("BUY CALL", "BULLISH"),
    )
    assert result.status == "CONSISTENT"
    assert result.semantic_status == "CONSISTENT"
    assert result.actionable is True
    assert result.vetoed is False


def test_non_actionable_decision_remains_consistent():
    result = reconcile_decision_intelligence(
        decision("WAIT"),
        intelligence("WAIT", "BULLISH"),
    )
    assert result.status == "CONSISTENT"
    assert result.semantic_status == "CONSISTENT"
    assert result.consistent is True
    assert result.actionable is False
    assert result.vetoed is False
