import streamlit as st

from app.utils.formatters import (
    format_strike,
)

from app.utils.badges import (
    dealer_gamma,
    market_mode,
    pressure,
)

# ==========================================================
# HELPERS
# ==========================================================

def _dealer(ctx):
    try:
        return ctx.analytics.get("dealer", {})
    except Exception:
        return {}


def _dealer_flow(ctx):
    try:
        return ctx.analytics.get("dealer_flow", {})
    except Exception:
        return {}


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    dealer = _dealer(ctx)
    flow = _dealer_flow(ctx)

    st.subheader("🏦 Dealer Analysis")

    # ------------------------------------------------------
    # Row 1
    # ------------------------------------------------------

    row1 = st.columns(4)

    row1[0].metric(
        "Dealer Gamma",
        dealer_gamma(
            dealer.get("dealer_gamma")
        )
    )

    row1[1].metric(
        "Market Mode",
        market_mode(
            dealer.get("market_mode")
        )
    )

    row1[2].metric(
        "Dealer Delta",
        flow.get("dealer_delta", "-")
    )

    row1[3].metric(
        "Dealer Hedging",
        flow.get("dealer_hedging", "-")
    )

    # ------------------------------------------------------
    # Row 2
    # ------------------------------------------------------

    row2 = st.columns(3)

    row2[0].metric(
        "Dealer Pressure",
        pressure(
            flow.get("dealer_pressure")
        )
    )

    row2[1].metric(
        "Support",
        format_strike(
            dealer.get("support")
        )
    )

    row2[2].metric(
        "Resistance",
        format_strike(
            dealer.get("resistance")
        )
    )