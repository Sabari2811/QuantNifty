import math

import streamlit as st


def _display_number(value, formatter):
    if value is None:
        return "UNAVAILABLE"
    try:
        if not math.isfinite(float(value)):
            return "UNAVAILABLE"
        return formatter(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"


def _analytics(ctx, key):
    try:
        value = ctx.analytics.get(key, {})
        return value if isinstance(value, dict) else {}
    except (AttributeError, TypeError):
        return {}


def _get_atm_strike(ctx):
    """Render the canonical ATM strike; never derive it in the UI."""
    expected_move = _analytics(ctx, "expected_move")
    return _display_number(
        expected_move.get("atm_strike"),
        lambda value: f"{float(value):.0f}",
    )


def _get_pcr(ctx):
    pcr = _analytics(ctx, "pcr")
    return _display_number(pcr.get("oi_pcr"), lambda value: f"{value:.2f}")


def _get_max_pain(ctx):
    max_pain = _analytics(ctx, "max_pain")
    return _display_number(max_pain.get("max_pain"), lambda value: f"{value:.0f}")


def _get_expected_move(ctx):
    expected_move = _analytics(ctx, "expected_move")
    low = expected_move.get("lower")
    high = expected_move.get("upper")
    if low is None or high is None:
        return "UNAVAILABLE"
    try:
        if not math.isfinite(float(low)) or not math.isfinite(float(high)):
            return "UNAVAILABLE"
        return f"{low:.2f} - {high:.2f}"
    except (TypeError, ValueError):
        return "UNAVAILABLE"


def _get_expiry(ctx):
    try:
        return ctx.expiry if ctx.expiry else "UNAVAILABLE"
    except AttributeError:
        return "UNAVAILABLE"


def show(ctx):
    """Present canonical market-summary values without recomputing analytics."""
    st.subheader("📈 Market Summary")

    row1 = st.columns(3)
    row2 = st.columns(3)

    row1[0].metric("Spot", _display_number(ctx.spot, lambda value: f"{value:,.2f}"))
    row1[1].metric("ATM Strike", _get_atm_strike(ctx))
    row1[2].metric("PCR", _get_pcr(ctx))
    row2[0].metric("Max Pain", _get_max_pain(ctx))
    row2[1].metric("Expected Move", _get_expected_move(ctx))
    row2[2].metric("Expiry", _get_expiry(ctx))
