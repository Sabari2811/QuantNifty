from tools.validate_live_session import _gate, _gate_is_hard_failure, _integrity_gate_status


def test_suspect_integrity_is_explicit_degraded_but_not_hard_failure():
    status, detail = _integrity_gate_status(invalid=False, suspect=True)

    gate = _gate(status, detail)

    assert gate["status"] == "DEGRADED"
    assert "analytics-usable" in gate["detail"]
    assert _gate_is_hard_failure("integrity", gate) is False


def test_invalid_integrity_is_hard_failure():
    status, detail = _integrity_gate_status(invalid=True, suspect=True)

    gate = _gate(status, detail)

    assert gate["status"] == "FAIL"
    assert _gate_is_hard_failure("integrity", gate) is True


def test_valid_integrity_passes():
    status, detail = _integrity_gate_status(invalid=False, suspect=False)

    gate = _gate(status, detail)

    assert gate["status"] == "PASS"
    assert _gate_is_hard_failure("integrity", gate) is False


def test_non_integrity_degraded_gate_remains_hard_failure():
    gate = _gate("DEGRADED", "unexpected degradation")

    assert _gate_is_hard_failure("freshness", gate) is True
