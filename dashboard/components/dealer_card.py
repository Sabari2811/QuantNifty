import streamlit as st


def render(dealer):
    """
    Professional Dealer Dashboard
    """

    st.subheader("🏦 Dealer Analytics")

    c1, c2, c3, c4 = st.columns(4)

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
        "Total GEX",
        f"{dealer.total_gex:,.0f}"
    )

    st.divider()

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Gamma Flip",
        "-" if dealer.gamma_flip is None else f"{dealer.gamma_flip:.0f}"
    )

    c6.metric(
        "Gamma Wall",
        "-" if dealer.gamma_wall is None else f"{dealer.gamma_wall:.0f}"
    )

    c7.metric(
        "Support",
        "-" if dealer.support is None else f"{dealer.support:.0f}"
    )

    c8.metric(
        "Resistance",
        "-" if dealer.resistance is None else f"{dealer.resistance:.0f}"
    )

    st.divider()

    c9, c10 = st.columns(2)

    c9.progress(
        dealer.mean_reversion_probability / 100,
        text=f"Mean Reversion : {dealer.mean_reversion_probability}%"
    )

    c10.progress(
        dealer.breakout_probability / 100,
        text=f"Breakout : {dealer.breakout_probability}%"
    )