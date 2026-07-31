import streamlit as st


def render(dashboard):
    """
    Market Regime Dashboard
    """

    dealer = dashboard.dealer
    probability = dashboard.probability

    st.subheader("🌍 Market Regime")

    c1, c2, c3, c4 = st.columns(4)

    # --------------------------------------------------
    # Row 1
    # --------------------------------------------------

    c1.metric(
        "Dealer Gamma",
        dealer.dealer_gamma
    )

    c2.metric(
        "Market Mode",
        dealer.market_mode
    )

    c3.metric(
        "Expected Volatility",
        dealer.expected_volatility
    )

    c4.metric(
        "Confidence",
        f"{probability['confidence']}%"
    )

    st.divider()

    c5, c6, c7, c8 = st.columns(4)

    # --------------------------------------------------
    # Row 2
    # --------------------------------------------------

    c5.metric(
        "Bullish",
        f"{probability['bullish_probability']}%"
    )

    c6.metric(
        "Bearish",
        f"{probability['bearish_probability']}%"
    )

    c7.metric(
        "Mean Reversion",
        f"{dealer.mean_reversion_probability}%"
    )

    c8.metric(
        "Breakout",
        f"{dealer.breakout_probability}%"
    )

    st.divider()

    c9, c10, c11 = st.columns(3)

    gamma_flip = (
        "-"
        if dealer.gamma_flip is None
        else f"{dealer.gamma_flip:.0f}"
    )

    gamma_wall = (
        "-"
        if dealer.gamma_wall is None
        else f"{dealer.gamma_wall:.0f}"
    )

    c9.metric(
        "Gamma Flip",
        gamma_flip
    )

    c10.metric(
        "Gamma Wall",
        gamma_wall
    )

    c11.metric(
        "Total GEX",
        f"{dealer.total_gex:,.2f}"
    )

    st.divider()