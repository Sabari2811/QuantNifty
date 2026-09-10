import math

import streamlit as st


def _display(value, default="N/A"):
    if value is None:
        return default
    if isinstance(value, float) and not math.isfinite(value):
        return default
    if value == "-":
        return default
    return str(value)


def render(trade_plan, signal=None):
    """Render the complete canonical trade plan in a compact decision layout."""
    trade_plan = trade_plan or {}
    trade_signal = trade_plan.get("signal", "WAIT")
    is_wait = trade_signal == "WAIT"

    st.subheader("🎯 Smart Trade Plan")

    if trade_signal == "BUY CALL":
        st.success("🟢 BUY CALL")
    elif trade_signal == "BUY PUT":
        st.error("🔴 BUY PUT")
    else:
        st.warning("🟡 WAIT")

    confidence = signal.get("confidence") if signal else None
    confidence_display = (
        "N/A — no actionable edge"
        if is_wait and confidence in (None, 0, 0.0)
        else _display(confidence)
    )

    # Keep recommendation, strike analytics, and entry plan visually adjacent.
    # No trade-plan field is removed; the same canonical values are simply
    # grouped into the three cards a trader reads left-to-right.
    c1, c2, c3 = st.columns([1.0, 1.35, 1.0], gap="small")

    with c1:
        st.markdown("### 🎯 Decision")
        st.metric(
            "Decision Confidence",
            confidence_display if confidence_display.startswith("N/A") else f"{confidence_display}%",
        )
        st.metric("Signal", trade_signal)
        st.caption("The decision remains WAIT when there is no actionable edge.")

        st.markdown("### 🌡 Market Volatility")
        st.info(
            f"ATR : {_display(trade_plan.get('atr'))}  |  "
            f"Current ATR Regime : {_display(trade_plan.get('volatility'))}"
        )

        st.markdown("### 📋 Why this Strike?")
        reasons = trade_plan.get("reasons") or []
        if not reasons:
            st.write("No strike-specific reasons because no strike is recommended.")
        else:
            for reason in reasons:
                st.write("✅", reason)

    with c2:
        st.markdown("### 🎯 Smart Strike Recommendation")
        strike = trade_plan.get("recommended_strike")
        has_recommendation = strike not in (None, "", "-")

        if not has_recommendation:
            st.info("No strike recommended for the current market condition (WAIT).")
            c21, c22, c23 = st.columns(3)
            c21.metric("Strike", "N/A")
            c22.metric("Strike Score", "N/A")
            c23.metric("Option Type", "N/A")
            c24, c25, c26 = st.columns(3)
            c24.metric("Delta", "N/A")
            c25.metric("IV", "N/A")
            c26.metric("NET GEX", "N/A")
            st.metric("ATR", _display(trade_plan.get("atr")))
        else:
            option_type = trade_plan.get("option_type", "")
            strike_display = (
                f"{int(strike)} {option_type}"
                if str(strike).isdigit()
                else f"{strike} {option_type}".strip()
            )
            c21, c22, c23 = st.columns(3)
            c21.metric("Strike", strike_display)
            c22.metric("Strike Score", f"{float(trade_plan.get('strike_score', 0)):.1f}")
            c23.metric("Delta", _display(trade_plan.get("delta")))
            c24, c25, c26 = st.columns(3)
            c24.metric("IV", _display(trade_plan.get("iv")))
            c25.metric("NET GEX", _display(trade_plan.get("gex")))
            c26.metric("ATR", _display(trade_plan.get("atr")))

    with c3:
        st.markdown("### 📍 Entry Plan")
        if is_wait:
            st.info("No entry, stop, target, or risk/reward is active while the decision is WAIT.")
        e1, e2 = st.columns(2)
        e1.metric("Entry", _display(trade_plan.get("entry")))
        e2.metric("Stop Loss", _display(trade_plan.get("stop_loss")))
        e3, e4 = st.columns(2)
        e3.metric("Risk Reward", _display(trade_plan.get("risk_reward")))
        e4.metric("Target 1", _display(trade_plan.get("target1")))
        st.metric("Target 2", _display(trade_plan.get("target2")))
