import streamlit as st

from app.utils.formatters import (
    format_strike,
    format_iv,
    format_percent,
    format_points,
)

from app.utils.badges import (
    volatility,
)


# ==========================================================
# Helpers
# ==========================================================

def _volatility(ctx):
    try:
        return ctx.analytics.get("volatility", {})
    except Exception:
        return {}


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    st.subheader("🌪️ Volatility Analysis")

    vol = _volatility(ctx)

    iv_skew = vol.get("iv_skew", {})
    iv_smile = vol.get("iv_smile", {})
    expected_move = vol.get("expected_move", {})

    # ======================================================
    # Summary
    # ======================================================

    st.markdown("### Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Volatility",
        volatility(
            vol.get("volatility_level")
        )
    )

    c2.metric(
        "Market Condition",
        vol.get("market_condition", "-")
    )

    c3.metric(
        "Expected Move %",
        format_percent(
            vol.get("expected_move_percent"),
            2
        )
    )

    st.divider()

    # ======================================================
    # Expected Move
    # ======================================================

    st.markdown("### Expected Move")

    e1, e2, e3 = st.columns(3)

    e1.metric(
        "Lower",
        format_strike(
            expected_move.get("lower")
        )
    )

    e2.metric(
        "Upper",
        format_strike(
            expected_move.get("upper")
        )
    )

    e3.metric(
        "Move (Pts)",
        format_points(
            vol.get("expected_move_points")
        )
    )

    st.divider()

    # ======================================================
    # ATR
    # ======================================================

    st.markdown("### ATR")

    a1, a2 = st.columns(2)

    a1.metric(
        "ATR",
        format_points(
            vol.get("atr_value")
        )
    )

    a2.metric(
        "Volatility Level",
        volatility(
            vol.get("volatility_level")
        )
    )

    st.divider()

    # ======================================================
    # IV Skew
    # ======================================================

    st.markdown("### IV Skew")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Average CE IV",
        format_iv(
            iv_skew.get("average_call_iv")
        )
    )

    c2.metric(
        "Average PE IV",
        format_iv(
            iv_skew.get("average_put_iv")
        )
    )

    c3.metric(
        "IV Skew",
        format_iv(
            iv_skew.get("iv_skew")
        )
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Bias",
        iv_skew.get("iv_bias", "-")
    )

    c5.metric(
        "Sentiment",
        iv_skew.get("market_sentiment", "-")
    )

    c6.metric(
        "IV State",
        volatility(
            iv_skew.get("volatility")
        )
    )

    st.divider()

    # ======================================================
    # IV Smile
    # ======================================================

    st.markdown("### IV Smile")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Dominant Side",
        iv_smile.get("dominant_side", "-")
    )

    s2.metric(
        "CE Peak Strike",
        format_strike(
            iv_smile.get("ce_peak_strike")
        )
    )

    s3.metric(
        "PE Peak Strike",
        format_strike(
            iv_smile.get("pe_peak_strike")
        )
    )

    s4, s5, s6 = st.columns(3)

    s4.metric(
        "CE Peak IV",
        format_iv(
            iv_smile.get("ce_peak_iv")
        )
    )

    s5.metric(
        "PE Peak IV",
        format_iv(
            iv_smile.get("pe_peak_iv")
        )
    )

    width = max(
        iv_smile.get("ce_smile_width", 0),
        iv_smile.get("pe_smile_width", 0)
    )

    s6.metric(
        "Smile Width",
        format_iv(width)
    )