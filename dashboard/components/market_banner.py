import streamlit as st


def _value(mapping, key, default="UNAVAILABLE"):
    if not mapping:
        return default
    value = mapping.get(key)
    return default if value is None else value


def render(dashboard):

    dealer = dashboard.dealer
    signal = dashboard.signal or {}
    trade = dashboard.trade_plan or {}
    probability = dashboard.probability or {}

    st.markdown("## 📊 Live Market Summary")

    c1, c2, c3, c4 = st.columns(4)

    signal_value = _value(signal, "signal")
    if signal_value == "BUY CALL":
        c1.success(signal_value)
    elif signal_value == "BUY PUT":
        c1.error(signal_value)
    else:
        c1.warning(signal_value)

    c2.metric("Spot", f"{dashboard.spot:.2f}")
    c3.metric("Dealer", dealer.dealer_gamma if dealer.dealer_gamma is not None else "UNAVAILABLE")
    c4.metric("Market", dealer.market_mode if dealer.market_mode is not None else "UNAVAILABLE")

    st.divider()

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Gamma Flip", dealer.gamma_flip if dealer.gamma_flip else "-")
    c6.metric("Gamma Wall", dealer.gamma_wall if dealer.gamma_wall else "-")

    bullish = _value(probability, "bullish_probability")
    c7.metric("Bullish %", f"{bullish}%" if bullish != "UNAVAILABLE" else "UNAVAILABLE")

    confidence = signal.get("confidence")
    c8.metric("Confidence", f"{confidence}%" if confidence is not None else "UNAVAILABLE")

    st.divider()

    c9, c10 = st.columns(2)
    recommended_strike = trade.get("recommended_strike")
    option_type = trade.get("option_type", "")
    c9.metric(
        "Recommended",
        f"{recommended_strike} {option_type}" if recommended_strike is not None else "UNAVAILABLE",
    )
    c10.metric("Risk Reward", trade.get("risk_reward", "UNAVAILABLE"))

    st.divider()
