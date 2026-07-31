import streamlit as st

from app.utils.formatters import (
    format_strike,
    format_gex,
)

# ==========================================================
# HELPERS
# ==========================================================

def _dealer(ctx):
    try:
        return ctx.analytics.get("dealer", {})
    except Exception:
        return {}


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    dealer = _dealer(ctx)

    st.subheader("🧲 Gamma Analysis")

    # ------------------------------------------------------
    # Row 1
    # ------------------------------------------------------

    row1 = st.columns(3)

    row1[0].metric(
        "Gamma Flip",
        format_strike(
            dealer.get("gamma_flip")
        )
    )

    row1[1].metric(
        "Gamma Wall",
        format_strike(
            dealer.get("gamma_wall")
        )
    )

    row1[2].metric(
        "Total GEX",
        format_gex(
            dealer.get("total_gex")
        )
    )

    # ------------------------------------------------------
    # Row 2
    # ------------------------------------------------------

    row2 = st.columns(2)

    row2[0].metric(
        "Call Wall",
        format_strike(
            dealer.get("call_wall")
        )
    )

    row2[1].metric(
        "Put Wall",
        format_strike(
            dealer.get("put_wall")
        )
    )