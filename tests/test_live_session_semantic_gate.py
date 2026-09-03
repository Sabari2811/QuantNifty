from tools.validate_live_session import _decision_intelligence_gate_ok


def _cycle(*, status="MATCH", consistent=True, semantic_status="CONSISTENT"):
    return {
        "decision_intelligence": {
            "status": status,
            "value": {
                "consistent": consistent,
                "semantic_status": semantic_status,
            },
        },
        "gaps": (),
    }


def test_semantic_gate_accepts_consistent_cycle():
    assert _decision_intelligence_gate_ok(_cycle()) is True


def test_semantic_gate_rejects_ui_match_with_conflict():
    assert _decision_intelligence_gate_ok(
        _cycle(consistent=False, semantic_status="CONFLICT")
    ) is False


def test_semantic_gate_rejects_ui_match_with_deferred_state():
    assert _decision_intelligence_gate_ok(
        _cycle(consistent=False, semantic_status="DEFERRED")
    ) is False


def test_semantic_gate_rejects_missing_reconciliation():
    assert _decision_intelligence_gate_ok({"decision_intelligence": None, "gaps": ()}) is False
