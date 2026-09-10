import math

import streamlit as st


def _money(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    return f"₹{number:,.0f}" if math.isfinite(number) else "UNAVAILABLE"


def _pct(value):
    try:
        number = float(value) * 100.0
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    return f"{number:.1f}%" if math.isfinite(number) else "UNAVAILABLE"


def render(risk):
    """Render the exact risk policy/state supplied by the execution layer."""
    st.subheader("🛡 Risk Management")

    if not risk:
        st.warning("Risk policy is unavailable; execution should remain blocked until it is restored.")
        return

    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Capital Per Trade", _money(risk.get("capital_per_trade")))
            st.metric(
                "Capital Utilization",
                f"{_pct(risk.get('capital_utilization'))} / {_pct(risk.get('capital_utilization_limit'))} limit",
            )
            st.metric("Max Daily Loss", _money(risk.get("max_daily_loss")))

        with col2:
            st.metric("Max Open Positions", risk.get("max_open_positions", "UNAVAILABLE"))
            st.metric("Cooldown", risk.get("cooldown", "UNAVAILABLE"))
            st.metric("Consecutive Loss Limit", risk.get("loss_limit", "UNAVAILABLE"))

        st.divider()
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Trades Today", risk.get("trades_today", "UNAVAILABLE"))
        s2.metric("Today's P&L", _money(risk.get("todays_pnl")))
        s3.metric("Consecutive Losses", risk.get("consecutive_losses", "UNAVAILABLE"))
        s4.metric("Open Positions", risk.get("open_positions", "UNAVAILABLE"))

        st.caption(
            f"Portfolio capital: {_money(risk.get('capital'))} · "
            f"Invested: {_money(risk.get('invested_amount'))} · "
            f"Max trades/day: {risk.get('max_trades_per_day', 'UNAVAILABLE')} · "
            f"Cooldown policy: {risk.get('cooldown_minutes', 'UNAVAILABLE')} min"
        )
