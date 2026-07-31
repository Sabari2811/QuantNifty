import streamlit as st

from app.utils.badges import (
    dealer_gamma,
    pressure,
    volatility,
)

from app.utils.formatters import (
    format_probability,
    format_strike,
)


# ==========================================================
# Helpers
# ==========================================================

def _analytics(ctx):

    return (
        ctx.analytics.get("signal", {}),
        ctx.analytics.get("dealer", {}),
        ctx.analytics.get("dealer_flow", {}),
        ctx.analytics.get("probability", {}),
        ctx.analytics.get("volatility", {}),
        ctx.analytics.get("liquidity", {}),
    )


# ==========================================================
# UI
# ==========================================================

def show(ctx):

    signal, dealer, flow, probability, vol, liquidity = _analytics(ctx)

    signal_name = signal.get("signal", "WAIT")
    confidence = signal.get(
        "confidence",
        probability.get("confidence", 0)
    )

    st.markdown("---")
    st.subheader("🏦 Institutional Trading Signal")

    # ------------------------------------------------------
    # Signal Banner
    # ------------------------------------------------------

    c1, c2 = st.columns([2, 1])

    with c1:

        if "CALL" in signal_name.upper():
            st.success(f"### 🟢 {signal_name}")

        elif "PUT" in signal_name.upper():
            st.error(f"### 🔴 {signal_name}")

        else:
            st.warning(f"### 🟡 {signal_name}")

    with c2:

        st.metric(
            "Confidence",
            format_probability(confidence)
        )

    st.divider()

    # ------------------------------------------------------
    # Market Snapshot
    # ------------------------------------------------------

    st.markdown("#### Market Snapshot")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Dealer Gamma",
        dealer_gamma(
            dealer.get("dealer_gamma")
        )
    )

    c2.metric(
        "Dealer Pressure",
        pressure(
            flow.get("dealer_pressure")
        )
    )

    c3.metric(
        "Volatility",
        volatility(
            vol.get("volatility_level")
        )
    )

    c4, c5 = st.columns(2)

    c4.metric(
        "Support",
        format_strike(
            liquidity.get("support")
        )
    )

    c5.metric(
        "Resistance",
        format_strike(
            liquidity.get("resistance")
        )
    )

    st.divider()

    # ------------------------------------------------------
    # Reasons
    # ------------------------------------------------------

    st.markdown("#### Institutional View")

    reasons = []

    if dealer.get("dealer_gamma") == "LONG":
        reasons.append("🟢 Dealers are Long Gamma (market stability).")
    else:
        reasons.append("🔴 Dealers are Short Gamma (higher market volatility).")

    if flow.get("dealer_pressure") == "BUY":
        reasons.append("🟢 Dealer positioning favors buying pressure.")
    elif flow.get("dealer_pressure") == "SELL":
        reasons.append("🔴 Dealer positioning favors selling pressure.")
    else:
        reasons.append("⚪ Dealer positioning is neutral.")

    breakout = dealer.get("breakout_probability", 0)
    mean_rev = dealer.get("mean_reversion_probability", 0)

    if breakout > mean_rev:
        reasons.append(
            f"📈 Breakout probability is higher ({breakout:.0f}%)."
        )
    else:
        reasons.append(
            f"🔄 Mean reversion probability is higher ({mean_rev:.0f}%)."
        )

    if vol.get("volatility_level") == "HIGH":
        reasons.append("🌪️ Elevated volatility. Consider wider stop-loss levels.")

    if liquidity.get("support") and liquidity.get("resistance"):
        reasons.append(
            f"🛡️ Key range: {format_strike(liquidity.get('support'))} → "
            f"{format_strike(liquidity.get('resistance'))}"
        )

    st.info("\n\n".join(reasons))