from app.pages.option_chain import _display_value, _flow_count, _recognized_flow_count


def test_display_value_preserves_real_zero_and_rejects_missing_values():
    assert _display_value({"value": 0}, "value") == 0
    assert _display_value({"value": 0.0}, "value") == 0.0
    assert _display_value({}, "value") == "—"
    assert _display_value({"value": None}, "value") == "—"


def test_display_value_rejects_non_finite_float():
    assert _display_value({"value": float("nan")}, "value") == "—"
    assert _display_value({"value": float("inf")}, "value") == "—"


def test_flow_count_does_not_turn_missing_into_zero():
    assert _flow_count({"long_buildup": 0}, "long_buildup") == 0
    assert _flow_count({}, "long_buildup") == "—"
    assert _flow_count({"long_buildup": "invalid"}, "long_buildup") == "—"


def test_recognized_flow_count_sums_only_available_numeric_fields():
    call = {"long_buildup": 2, "short_buildup": 0}
    put = {"long_unwinding": 3}
    assert _recognized_flow_count(call, put) == 5
