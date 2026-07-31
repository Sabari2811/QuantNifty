import streamlit as st


def show(ctx):

    regime = getattr(ctx, "regime", None)
    decision = getattr(ctx, "decision", None)

    st.title("📈 QuantNifty")

    if regime is None:

        st.warning("Market Regime Unavailable")
        return

    # --------------------------------------------------
    # Trend Icon
    # --------------------------------------------------

    trend = str(getattr(regime, "trend", "NEUTRAL")).upper()

    if trend == "BULLISH":
        trend_icon = "🟢"
    elif trend == "BEARISH":
        trend_icon = "🔴"
    else:
        trend_icon = "🟡"

    # --------------------------------------------------
    # Runtime Status
    # --------------------------------------------------

    status = getattr(ctx, "runtime_status", "READY")

    if status == "RUNNING":
        status_icon = "🟢"
    elif status == "READY":
        status_icon = "🟡"
    elif status == "ERROR":
        status_icon = "🔴"
    else:
        status_icon = "⚪"

    # --------------------------------------------------
    # Trade Confidence
    # --------------------------------------------------

    trade_confidence = 0

    if (
        decision is not None
        and getattr(decision, "signal", None) is not None
    ):
        trade_confidence = getattr(
            decision.signal,
            "confidence",
            0
        )

    # --------------------------------------------------
    # Header KPIs
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Market Regime",
            getattr(regime, "regime", "-")
        )

    with col2:

        st.metric(
            "Trend",
            f"{trend_icon} {trend}"
        )

    with col3:

        st.metric(
            "Trade Confidence",
            f"{trade_confidence}%"
        )

    with col4:

        st.metric(
            "Runtime",
            f"{status_icon} {status}"
        )

    # --------------------------------------------------
    # Footer Information
    # --------------------------------------------------

    info1, info2, info3 = st.columns(3)

    with info1:

        st.caption(
            f"Spot : {ctx.spot:,.2f}"
        )

    with info2:

        st.caption(
            f"Volatility : {getattr(regime, 'volatility', '-')}"
        )

    with info3:

        timestamp = getattr(ctx, "timestamp", "")

        if timestamp:
            st.caption(
                f"Updated : {timestamp}"
            )

    st.divider()