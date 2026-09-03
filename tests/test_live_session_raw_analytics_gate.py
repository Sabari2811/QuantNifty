from tools.validate_live_session import _raw_analytics_gate_ok


def test_raw_analytics_gate_requires_all_cycles_to_pass():
    assert _raw_analytics_gate_ok([
        {"raw_analytics": {"status": "PASS"}},
        {"raw_analytics": {"status": "PASS"}},
    ]) is True


def test_raw_analytics_gate_rejects_any_cycle_gap():
    assert _raw_analytics_gate_ok([
        {"raw_analytics": {"status": "PASS"}},
        {"raw_analytics": {"status": "GAP"}},
    ]) is False


def test_raw_analytics_gate_rejects_missing_evidence():
    assert _raw_analytics_gate_ok([]) is False
    assert _raw_analytics_gate_ok([{"raw_analytics": None}]) is False
