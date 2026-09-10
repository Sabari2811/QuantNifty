import math

import streamlit as st


def _display(value, suffix="-", default="UNAVAILABLE"):
    if value is None:
        return default
    if isinstance(value, float) and not math.isfinite(value):
        return default
    return f"{value}{suffix}" if suffix != "-" else f"{value}"


def _confidence_display(signal, confidence):
    if signal == "WAIT" and confidence in (None, 0, 0.0):
        return "N/A — no actionable edge"
    return _display(confidence, "%")


def render(decision, dealer):
    """Render canonical decision fields without recomputing the signal."""
    st.subheader("🎯 Trade Signal")

    decision = decision or {}
    dealer = dealer

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
    c1.metric("Bullish", _display(bullish, "%"))
    c2.metric("Bearish", _display(bearish, "%"))
    c3.metric("Decision Confidence", _confidence_display(signal, confidence))

    reasons = decision.get("reasons", ())
    if reasons:
        st.write("### Reasons")
        for reason in reasons:
            st.write(f"✅ {reason}")

    dealer_gamma = getattr(dealer, "dealer_gamma", None)
    market_mode = getattr(dealer, "market_mode", None)
    expected_volatility = getattr(dealer, "expected_volatility", None)

    st.info(
        f"""
Gamma Position : **{_display(dealer_gamma)}**

Market Mode : **{_display(market_mode)}**

Expected Volatility : **{_display(expected_volatility)}**
"""
    )

    st.divider()
