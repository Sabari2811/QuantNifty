import pandas as pd

from tools.validate_live_oi_consecutive import _expected_flow


def test_expected_flow_all_four_types_and_no_change():
    assert _expected_flow(1.0, 10) == "LONG_BUILDUP"
    assert _expected_flow(-1.0, 10) == "SHORT_BUILDUP"
    assert _expected_flow(1.0, -10) == "SHORT_COVERING"
    assert _expected_flow(-1.0, -10) == "LONG_UNWINDING"
    assert _expected_flow(0.0, 0) == "NO_CHANGE"


def test_expected_flow_missing_delta_is_unknown():
    assert _expected_flow(float("nan"), 10) == "UNKNOWN"
    assert _expected_flow(1.0, float("nan")) == "UNKNOWN"
