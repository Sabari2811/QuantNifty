import streamlit as st


def render(
    probability,
    dealer
):
    """
    Trade Signal Card
    """

    st.subheader("🎯 Trade Signal")

    bullish = probability["bullish_probability"]
    bearish = probability["bearish_probability"]
    confidence = probability["confidence"]

    # ======================================================
    # Signal
    # ======================================================

    if bullish >= 70:

        signal = "🟢 BUY CALL"

    elif bearish >= 70:

        signal = "🔴 BUY PUT"

    else:

        signal = "🟡 WAIT"

    st.success(signal)

    # ======================================================
    # Metrics
    # ======================================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Bullish",
            f"{bullish}%"
        )

    with c2:

        st.metric(
            "Bearish",
            f"{bearish}%"
        )

    with c3:

        st.metric(
            "Confidence",
            f"{confidence}%"
        )

    # ======================================================
    # Reasons
    # ======================================================

    st.write("### Reasons")

    for reason in probability["reasons"]:

        st.write(f"✅ {reason}")

    # ======================================================
    # Dealer Summary
    # ======================================================

    st.info(

        f"""
Dealer Gamma : **{dealer.dealer_gamma}**

Market Mode : **{dealer.market_mode}**

Expected Volatility : **{dealer.expected_volatility}**
"""

    )

    st.divider()