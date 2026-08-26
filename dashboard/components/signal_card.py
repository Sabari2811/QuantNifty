import streamlit as st


def render(decision, dealer):
    """Render canonical decision fields without recomputing the signal."""

    st.subheader("🎯 Trade Signal")

    bullish = decision.get("bullish_probability")
    bearish = decision.get("bearish_probability")
    confidence = decision.get("confidence")
    signal = decision.get("signal")

    if signal is None:
        st.info("Trade signal unavailable for this runtime cycle.")
        return

    if signal == "BUY CALL":
        st.success("🟢 BUY CALL")
    elif signal == "BUY PUT":
        st.error("🔴 BUY PUT")
    else:
        st.warning(f"🟡 {signal}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Bullish", "-" if bullish is None else f"{bullish}%")
    c2.metric("Bearish", "-" if bearish is None else f"{bearish}%")
    c3.metric("Confidence", "-" if confidence is None else f"{confidence}%")

    reasons = decision.get("reasons", ())
    if reasons:
        st.write("### Reasons")
        for reason in reasons:
            st.write(f"✅ {reason}")

    st.info(
        f"""
Dealer Gamma : **{dealer.dealer_gamma}**

Market Mode : **{dealer.market_mode}**

Expected Volatility : **{dealer.expected_volatility}**
"""
    )

    st.divider()
