import streamlit as st

from app.utils.formatters import (
    format_probability,
)

# ==========================================================
# HELPERS
# ==========================================================

def _probability(ctx):
    try:
        return ctx.analytics.get("probability", {})
    except Exception:
        return {}


def _dealer(ctx):
    try:
        return ctx.analytics.get("dealer", {})
    except Exception:
        return {}


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    probability = _probability(ctx)
    dealer = _dealer(ctx)

    st.subheader("📊 Probability Analysis")

    # ------------------------------------------------------
    # Row 1
    # ------------------------------------------------------

    row1 = st.columns(3)

    row1[0].metric(
        "Bullish Probability",
        format_probability(
            probability.get("bullish_probability")
        )
    )

    row1[1].metric(
        "Bearish Probability",
        format_probability(
            probability.get("bearish_probability")
        )
    )

    row1[2].metric(
        "Confidence",
        format_probability(
            probability.get("confidence")
        )
    )

    # ------------------------------------------------------
    # Row 2
    # ------------------------------------------------------

    row2 = st.columns(2)

    row2[0].metric(
        "Mean Reversion",
        format_probability(
            dealer.get("mean_reversion_probability")
        )
    )

    row2[1].metric(
        "Breakout",
        format_probability(
            dealer.get("breakout_probability")
        )
    )