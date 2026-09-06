import math

import streamlit as st


def _display_percent(value):
    """Render a known percentage or an explicit unknown marker."""
    if value is None:
        return "—"
    try:
        if math.isnan(float(value)):
            return "—"
    except (TypeError, ValueError):
        pass
    return f"{value}%"


def render(dashboard):
    """
    KPI Cards
    """

    dealer = dashboard.dealer
    probability = dashboard.probability

    # Do not default missing canonical values to 0: zero is a real value and
    # must not be fabricated when the backend value is unavailable.
    bullish = probability.get("bullish_probability")
    confidence = probability.get("confidence")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    # ======================================================
    # Spot
    # ======================================================

    c1.metric(
        "Spot",
        f"{dashboard.spot:,.2f}"
    )

    # ======================================================
    # Dealer Gamma
    # ======================================================

    c2.metric(
        "Dealer",
        dealer.dealer_gamma
    )

    # ======================================================
    # Market Mode
    # ======================================================

    c3.metric(
        "Market",
        dealer.market_mode
    )

    # ======================================================
    # Bullish Probability
    # ======================================================

    c4.metric(
        "Bullish %",
        _display_percent(bullish)
    )

    # ======================================================
    # Confidence
    # ======================================================

    c5.metric(
        "Confidence",
        _display_percent(confidence)
    )

    # ======================================================
    # Provider
    # ======================================================

    c6.metric(
        "Provider",
        dashboard.provider.upper()
    )

    st.divider()
