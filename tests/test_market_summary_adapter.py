from types import SimpleNamespace

from dashboard.market_summary_adapter import adapt_market_summary


def _dashboard():
    return SimpleNamespace(
        spot=24334.55,
        expiry="09/01/2026 14:00",
        expected_move={
            "spot": 24334.55,
            "atm_strike": 24350,
            "expected_move": 228.40,
            "lower": 24106.15,
            "upper": 24562.95,
            "method": "ATM_STRADDLE",
        },
        max_pain={
            "max_pain": 24200,
            "call_oi": 123,
            "put_oi": 456,
            "total_oi": 579,
        },
        pcr={
            "oi_pcr": 0.97,
            "volume_pcr": 1.02,
            "sentiment": "NEUTRAL",
        },
    )


def test_market_summary_uses_canonical_dashboard_fields():
    summary = adapt_market_summary(_dashboard())

    assert summary == {
        "spot": 24334.55,
        "atm_strike": 24350,
        "pcr": 0.97,
        "max_pain": 24200,
        "expected_move": 228.40,
        "expected_move_lower": 24106.15,
        "expected_move_upper": 24562.95,
        "expiry": "09/01/2026 14:00",
    }


def test_market_summary_does_not_invent_missing_analytics():
    dashboard = _dashboard()
    dashboard.expected_move = {}
    dashboard.max_pain = {}
    dashboard.pcr = {}

    summary = adapt_market_summary(dashboard)

    assert summary["spot"] == 24334.55
    assert summary["expiry"] == "09/01/2026 14:00"
    assert summary["atm_strike"] is None
    assert summary["pcr"] is None
    assert summary["max_pain"] is None
    assert summary["expected_move"] is None
    assert summary["expected_move_lower"] is None
    assert summary["expected_move_upper"] is None
