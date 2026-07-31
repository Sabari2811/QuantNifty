import streamlit as st


def render(dashboard):

    dealer = dashboard.dealer
    signal = dashboard.signal
    trade = dashboard.trade_plan
    probability = dashboard.probability

    st.markdown("## 📊 Live Market Summary")

    c1, c2, c3, c4 = st.columns(4)

    # ----------------------------------------

    if signal["signal"] == "BUY CALL":
        c1.success(signal["signal"])

    elif signal["signal"] == "BUY PUT":
        c1.error(signal["signal"])

    else:
        c1.warning(signal["signal"])

    # ----------------------------------------

    c2.metric(
        "Spot",
        f"{dashboard.spot:.2f}"
    )

    # ----------------------------------------

    c3.metric(
        "Dealer",
        dealer.dealer_gamma
    )

    # ----------------------------------------

    c4.metric(
        "Market",
        dealer.market_mode
    )

    st.divider()

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Gamma Flip",
        dealer.gamma_flip if dealer.gamma_flip else "-"
    )

    c6.metric(
        "Gamma Wall",
        dealer.gamma_wall if dealer.gamma_wall else "-"
    )

    c7.metric(
        "Bullish %",
        f"{probability['bullish_probability']}%"
    )

    c8.metric(
        "Confidence",
        f"{signal['confidence']}%"
    )

    st.divider()

    c9, c10 = st.columns(2)

    c9.metric(
        "Recommended",
        f"{trade['recommended_strike']} {trade.get('option_type', '')}"
    )

    c10.metric(
        "Risk Reward",
        trade["risk_reward"]
    )

    st.divider()