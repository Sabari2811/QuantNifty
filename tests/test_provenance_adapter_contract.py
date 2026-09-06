from dashboard.provenance_adapter import option_chain_quality_state, adapt_provenance


def test_option_chain_quality_is_unavailable_when_required_statuses_are_missing():
    assert option_chain_quality_state(None) == "UNAVAILABLE"
    assert option_chain_quality_state({}) == "UNAVAILABLE"
    assert option_chain_quality_state({"coverage_status": "COMPLETE"}) == "UNAVAILABLE"
    assert option_chain_quality_state({"integrity_status": "VALID"}) == "UNAVAILABLE"


def test_option_chain_quality_preserves_degraded_and_ready_states():
    assert option_chain_quality_state({"coverage_status": "PARTIAL", "integrity_status": "VALID"}) == "DEGRADED"
    assert option_chain_quality_state({"coverage_status": "COMPLETE", "integrity_status": "SUSPECT"}) == "DEGRADED"
    assert option_chain_quality_state({"coverage_status": "COMPLETE", "integrity_status": "INVALID"}) == "DEGRADED"
    assert option_chain_quality_state({"coverage_status": "COMPLETE", "integrity_status": "VALID"}) == "READY"


def test_missing_runtime_provenance_is_not_synthesized():
    result = adapt_provenance(None)
    assert result["spot"] is None
    assert result["option_chain"] is None
    assert result["option_chain_quality"] == "UNAVAILABLE"
    assert result["candles"] is None
    assert result["coverage_ratio"] is None
    assert result["complete"] is False
