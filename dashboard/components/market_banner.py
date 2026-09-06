import math

import streamlit as st

from dashboard.decision_adapter import adapt_decision


def _value(mapping, key, default="UNAVAILABLE"):
    if not mapping:
        return default
    value = mapping.get(key)
    return default if value is None else value


def _display_number(value, decimals=2, default="UNAVAILABLE"):
    if value is None:
        return default
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numeric):
        return default
    return f"{numeric:,.{decimals}f}"


def render(dashboard):

    dealer = dashboard.dealer
    decision = adapt_decision(dashboard)
    trade = dashboard.trade_plan or {}

    st.markdown("## 📊 Live Market Summary")

    c1, c2, c3, c4 = st.columns(4)

    signal_value = decision.get("signal")
    if signal_value is None:
        signal_value = "UNAVAILABLE"
    if signal_value == "BUY CALL":
        c1.success(signal_value)
    elif signal_value == "BUY PUT":
        c1.error(signal_value)
    else:
        c1.warning(signal_value)

    c2.metric("Spot", _display_number(dashboard.spot))
    c3.metric("Dealer", _value({"value": dealer.dealer_gamma}, "value"))
    c4.metric("Market", _value({"value": dealer.market_mode}, "value"))

    st.divider()

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Gamma Flip", _display_number(dealer.gamma_flip, decimals=0))
    c6.metric("Gamma Wall", _display_number(dealer.gamma_wall, decimals=0))

    bullish = decision.get("bullish_probability")
    c7.metric("Bullish %", _display_number(bullish, decimals=1, default="UNAVAILABLE") + ("%" if bullish is not None and _display_number(bullish, decimals=1, default="UNAVAILABLE") != "UNAVAILABLE" else ""))

    confidence = decision.get("confidence")
    c8.metric("Confidence", _display_number(confidence, decimals=1, default="UNAVAILABLE") + ("%" if confidence is not None and _display_number(confidence, decimals=1, default="UNAVAILABLE") != "UNAVAILABLE" else ""))

    st.divider()

    c9, c10 = st.columns(2)
    recommended_strike = trade.get("recommended_strike")
    option_type = trade.get("option_type") or ""
    c9.metric(
        "Recommended",
        f"{recommended_strike} {option_type}" if recommended_strike is not None else "UNAVAILABLE",
    )
    risk_reward = trade.get("risk_reward")
    c10.metric("Risk Reward", risk_reward if risk_reward is not None else "UNAVAILABLE")

    st.divider()
