import math

import streamlit as st


# ==========================================================
# HELPERS
# ==========================================================

def _display_number(value, formatter):
    if value is None:
        return "UNAVAILABLE"
    try:
        if not math.isfinite(float(value)):
            return "UNAVAILABLE"
        return formatter(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"


def _find_atm(ctx):
    try:
        df = ctx.greeks_df
        spot = ctx.spot
        if df is None or df.empty or spot is None or not math.isfinite(float(spot)):
            return "UNAVAILABLE"
        return min(df["Strike"], key=lambda x: abs(x - spot))
    except Exception:
        return "UNAVAILABLE"


def _get_pcr(ctx):
    try:
        pcr = ctx.analytics.get("pcr", {})
        return _display_number(pcr.get("oi_pcr"), lambda value: f"{value:.2f}")
    except Exception:
        return "UNAVAILABLE"


def _get_max_pain(ctx):
    try:
        mp = ctx.analytics.get("max_pain", {})
        return _display_number(mp.get("max_pain"), lambda value: f"{value:.0f}")
    except Exception:
        return "UNAVAILABLE"


def _get_expected_move(ctx):
    try:
        em = ctx.analytics.get("expected_move", {})
        low = em.get("lower")
        high = em.get("upper")
        if low is None or high is None:
            return "UNAVAILABLE"
        if not math.isfinite(float(low)) or not math.isfinite(float(high)):
            return "UNAVAILABLE"
        return f"{low:.2f} - {high:.2f}"
    except Exception:
        return "UNAVAILABLE"


def _get_expiry(ctx):
    try:
        return ctx.expiry if ctx.expiry else "UNAVAILABLE"
    except Exception:
        return "UNAVAILABLE"


# ==========================================================
# UI
# ==========================================================

def show(ctx):
    st.subheader("📈 Market Summary")

    row1 = st.columns(3)
    row2 = st.columns(3)

    row1[0].metric(
        "Spot",
        _display_number(ctx.spot, lambda value: f"{value:,.2f}")
    )

    row1[1].metric(
        "ATM Strike",
        _find_atm(ctx)
    )

    row1[2].metric(
        "PCR",
        _get_pcr(ctx)
    )

    row2[0].metric(
        "Max Pain",
        _get_max_pain(ctx)
    )

    row2[1].metric(
        "Expected Move",
        _get_expected_move(ctx)
    )

    row2[2].metric(
        "Expiry",
        _get_expiry(ctx)
    )
