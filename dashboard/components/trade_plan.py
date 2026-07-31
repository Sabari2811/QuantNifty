import streamlit as st


def render(trade_plan, signal=None):
    """
    QuantNifty Trade Plan Card V2
    """

    st.subheader("🎯 Smart Trade Plan")

    trade_signal = trade_plan["signal"]

    # =====================================================
    # Signal Banner
    # =====================================================

    if trade_signal == "BUY CALL":

        st.success("🟢 BUY CALL")

    elif trade_signal == "BUY PUT":

        st.error("🔴 BUY PUT")

    else:

        st.warning("🟡 WAIT")

    # =====================================================
    # Confidence
    # =====================================================

    if signal:

        confidence = signal.get("confidence", 0)

        st.metric(
            "Confidence",
            f"{confidence}%"
        )

    st.divider()

    # =====================================================
    # Smart Strike
    # =====================================================

    st.markdown("### 🎯 Smart Strike Recommendation")

    c1, c2, c3 = st.columns(3)

    strike = trade_plan["recommended_strike"]

    option_type = trade_plan.get(
        "option_type",
        ""
    )

    strike_display = (
        "-"
        if strike == "-"
        else f"{int(strike)} {option_type}"
    )

    c1.metric(
        "Strike",
        strike_display
    )

    c2.metric(
        "Strike Score",
        f"{trade_plan.get('strike_score',0):.1f}"
    )

    delta = trade_plan.get("delta")

    c3.metric(
        "Delta",
        "-"
        if delta is None
        else f"{delta:.3f}"
    )

    c4, c5, c6 = st.columns(3)

    iv = trade_plan.get("iv")

    c4.metric(
        "IV",
        "-"
        if iv is None
        else f"{iv:.3f}"
    )

    gex = trade_plan.get("gex")

    c5.metric(
        "NET GEX",
        "-"
        if gex is None
        else f"{gex:.2f}"
    )

    c6.metric(
        "ATR",
        trade_plan["atr"]
    )

    st.divider()

    # =====================================================
    # Entry Plan
    # =====================================================

    st.markdown("### 📍 Entry Plan")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Entry",
        trade_plan["entry"]
    )

    c2.metric(
        "Stop Loss",
        trade_plan["stop_loss"]
    )

    c3.metric(
        "Risk Reward",
        trade_plan["risk_reward"]
    )

    c4, c5 = st.columns(2)

    c4.metric(
        "Target 1",
        trade_plan["target1"]
    )

    c5.metric(
        "Target 2",
        trade_plan["target2"]
    )

    st.divider()

    # =====================================================
    # Volatility
    # =====================================================

    st.markdown("### 🌡 Market Volatility")

    st.info(

        f"ATR : {trade_plan['atr']}    |    "

        f"Volatility : {trade_plan['volatility']}"

    )

    # =====================================================
    # Reasons
    # =====================================================

    st.markdown("### 📋 Why this Strike?")

    for reason in trade_plan["reasons"]:

        st.write("✅", reason)

    st.divider()