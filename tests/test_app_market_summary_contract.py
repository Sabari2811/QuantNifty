from types import SimpleNamespace

from app.components.market_summary import _get_atm_strike, _get_expected_move, _get_max_pain, _get_pcr


def _ctx(**overrides):
    values = {
        "spot": None,
        "analytics": {},
        "expiry": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_market_summary_fails_closed_for_missing_core_values():
    ctx = _ctx()
    assert _get_atm_strike(ctx) == "UNAVAILABLE"
    assert _get_pcr(ctx) == "UNAVAILABLE"
    assert _get_max_pain(ctx) == "UNAVAILABLE"
    assert _get_expected_move(ctx) == "UNAVAILABLE"


def test_market_summary_preserves_valid_zero_values():
    ctx = _ctx(
        spot=0,
        analytics={
            "expected_move": {"atm_strike": 0, "lower": 0, "upper": 0},
            "pcr": {"oi_pcr": 0},
            "max_pain": {"max_pain": 0},
        },
        expiry="2026-09-10",
    )
    assert _get_atm_strike(ctx) == "0"
    assert _get_pcr(ctx) == "0.00"
    assert _get_max_pain(ctx) == "0"
    assert _get_expected_move(ctx) == "0.00 - 0.00"
    assert ctx.expiry == "2026-09-10"


def test_market_summary_does_not_recompute_atm_from_greeks():
    ctx = _ctx(
        spot=25000,
        analytics={"expected_move": {"lower": 24900, "upper": 25100}},
    )
    assert _get_atm_strike(ctx) == "UNAVAILABLE"
