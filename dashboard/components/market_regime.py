import streamlit as st


def _display(value, suffix=""):
    return "UNAVAILABLE" if value is None else f"{value}{suffix}"


def _confidence(value, signal):
    if signal == "WAIT" and value in (None, 0, 0.0):
        return "N/A — no actionable edge"
    return _display(value, "%")


def _display_number(value, decimals=2):
    return "UNAVAILABLE" if value is None else f"{value:,.{decimals}f}"


def render(dashboard):
    """Render the canonical market-regime artifact."""
    dealer = dashboard.dealer
    probability = dashboard.probability or {}
    signal = (dashboard.signal or {}).get("signal")

    st.subheader("🌍 Market Regime")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gamma Position", _display(dealer.dealer_gamma))
    c2.metric("Market Mode", _display(dealer.market_mode))
    c3.metric("Expected Volatility", _display(dealer.expected_volatility))
    c4.metric("Regime Confidence", _confidence(probability.get("confidence"), signal))

    st.divider()

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Bullish", _display(probability.get("bullish_probability"), "%"))
    c6.metric("Bearish", _display(probability.get("bearish_probability"), "%"))
    c7.metric("Mean Reversion", _display(dealer.mean_reversion_probability, "%"))
    c8.metric("Breakout", _display(dealer.breakout_probability, "%"))

    st.divider()

    c9, c10, c11 = st.columns(3)
    gamma_flip = "-" if dealer.gamma_flip is None else f"{dealer.gamma_flip:.0f}"
    gamma_wall = "-" if dealer.gamma_wall is None else f"{dealer.gamma_wall:.0f}"
    c9.metric("Gamma Flip", gamma_flip)
    c10.metric("Gamma Wall", gamma_wall)
    c11.metric("Total GEX", _display_number(dealer.total_gex))

    st.divider()
