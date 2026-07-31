import streamlit as st


def render(dashboard):
    """
    KPI Cards
    """

    dealer = dashboard.dealer
    probability = dashboard.probability

    bullish = probability.get(
        "bullish_probability",
        0
    )

    confidence = probability.get(
        "confidence",
        0
    )

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
        f"{bullish}%"
    )

    # ======================================================
    # Confidence
    # ======================================================

    c5.metric(
        "Confidence",
        f"{confidence}%"
    )

    # ======================================================
    # Provider
    # ======================================================

    c6.metric(
        "Provider",
        dashboard.provider.upper()
    )

    st.divider()