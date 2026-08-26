"""Canonical backend -> dashboard mapping for market-summary fields."""


def adapt_market_summary(dashboard) -> dict:
    """Return only values already authoritative on one DashboardData cycle.

    This adapter deliberately performs no analytics and no fallback calculations.
    Every value is copied from the canonical DashboardData/runtime mapping so the
    UI cannot silently derive a competing value for the same field.
    """
    expected_move = dashboard.expected_move or {}
    max_pain = dashboard.max_pain or {}
    pcr = dashboard.pcr or {}

    return {
        "spot": dashboard.spot,
        "atm_strike": expected_move.get("atm_strike"),
        "expected_move": expected_move.get("expected_move"),
        "expected_move_lower": expected_move.get("lower"),
        "expected_move_upper": expected_move.get("upper"),
        "expected_move_method": expected_move.get("method"),
        "pcr": pcr.get("oi_pcr"),
        "max_pain": max_pain.get("max_pain"),
        "expiry": dashboard.expiry,
    }
