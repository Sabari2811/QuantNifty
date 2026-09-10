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
    """Render the canonical trade plan without implying a trade when WAIT."""
    trade_plan = trade_plan or {}
    st.subheader("🎯 Smart Trade Plan")

    trade_signal = trade_plan.get("signal", "WAIT")
    is_wait = trade_signal == "WAIT"

    if trade_signal == "BUY CALL":
        st.success("🟢 BUY CALL")
    elif trade_signal == "BUY PUT":
        st.error("🔴 BUY PUT")
    else:
        st.warning("🟡 WAIT")

    if signal:
        confidence = signal.get("confidence")
        confidence_display = "N/A — no actionable edge" if is_wait and (confidence in (None, 0, 0.0)) else _display(confidence)
        st.metric("Decision Confidence", confidence_display if confidence_display.startswith("N/A") else f"{confidence_display}%")

    st.divider()

    st.markdown("### 🎯 Smart Strike Recommendation")
    strike = trade_plan.get("recommended_strike")
    has_recommendation = strike not in (None, "", "-")

    if not has_recommendation:
        st.info("No strike recommendation for this cycle because the canonical decision is WAIT.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Strike", "N/A")
        c2.metric("Strike Score", "N/A")
        c3.metric("Option Type", "N/A")
        c4, c5, c6 = st.columns(3)
        c4.metric("Delta", "N/A")
        c5.metric("IV", "N/A")
        c6.metric("NET GEX", "N/A")
    else:
        option_type = trade_plan.get("option_type", "")
        strike_display = f"{int(strike)} {option_type}" if str(strike).isdigit() else f"{strike} {option_type}".strip()
        c1, c2, c3 = st.columns(3)
        c1.metric("Strike", strike_display)
        c2.metric("Strike Score", f"{float(trade_plan.get('strike_score', 0)):.1f}")
        c3.metric("Delta", _display(trade_plan.get("delta")))
        c4, c5, c6 = st.columns(3)
        c4.metric("IV", _display(trade_plan.get("iv")))
        c5.metric("NET GEX", _display(trade_plan.get("gex")))
        c6.metric("ATR", _display(trade_plan.get("atr")))

    st.divider()

    st.markdown("### 📍 Entry Plan")
    if is_wait:
        st.info("No entry, stop, target, or risk/reward is active while the decision is WAIT.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Entry", _display(trade_plan.get("entry")))
    c2.metric("Stop Loss", _display(trade_plan.get("stop_loss")))
    c3.metric("Risk Reward", _display(trade_plan.get("risk_reward")))
    c4, c5 = st.columns(2)
    c4.metric("Target 1", _display(trade_plan.get("target1")))
    c5.metric("Target 2", _display(trade_plan.get("target2")))

    st.divider()

    st.markdown("### 🌡 Market Volatility")
    st.info(
        f"ATR : {_display(trade_plan.get('atr'))}    |    "
        f"Current ATR Regime : {_display(trade_plan.get('volatility'))}"
    )

    st.markdown("### 📋 Why this Strike?")
    reasons = trade_plan.get("reasons") or []
    if not reasons:
        st.write("No strike-specific reasons because no strike is recommended.")
    else:
        for reason in reasons:
            st.write("✅", reason)

    st.divider()
