import streamlit as st

from app.services.live_service import LiveService


def show():

    service = LiveService()

    st.title("⚙ Runtime")

    # ==========================================================
    # Controls
    # ==========================================================

    c1, c2 = st.columns(2)

    with c1:
        if st.button("▶ Start Runtime", use_container_width=True):
            service.start()

    with c2:
        if st.button("■ Stop Runtime", use_container_width=True):
            service.stop()

    ctx = service.get_context()

    st.divider()

    # ==========================================================
    # Runtime Status
    # ==========================================================

    st.subheader("Runtime Status")

    a, b, c, d = st.columns(4)

    a.metric("Status", ctx.runtime_status)
    b.metric("Cycle", ctx.cycle_no)
    c.metric("Spot", round(ctx.spot, 2))
    d.metric("Updated", ctx.timestamp)

    # ==========================================================
    # Trade Engine
    # ==========================================================

    st.divider()

    st.subheader("Trade Engine")

    x, y = st.columns(2)

    x.metric(
        "Trade Status",
        ctx.trade_status or "-"
    )

    y.metric(
        "Block Reason",
        ctx.trade_block_reason or "-"
    )

    # ==========================================================
    # Portfolio
    # ==========================================================

    st.divider()

    st.subheader("Portfolio")

    portfolio = ctx.portfolio

    if portfolio is None:

        st.info("Portfolio not initialized.")

    else:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Available Cash",
            f"₹{portfolio.available_cash:,.2f}"
        )

        c2.metric(
            "Invested",
            f"₹{portfolio.invested_amount:,.2f}"
        )

        c3.metric(
            "Realized P&L",
            f"₹{portfolio.realized_pnl:,.2f}"
        )

        c4.metric(
            "Unrealized P&L",
            f"₹{portfolio.unrealized_pnl:,.2f}"
        )

    # ==========================================================
    # Active Position
    # ==========================================================

    st.divider()

    st.subheader("Open Position")

    if ctx.position is None:

        st.info("No active position.")

    else:

        st.json(vars(ctx.position))

    # ==========================================================
    # Last Trade
    # ==========================================================

    st.divider()

    st.subheader("Last Completed Trade")

    if ctx.last_trade is None:

        st.info("No completed trades.")

    else:

        st.json(vars(ctx.last_trade))

    # ==========================================================
    # Statistics
    # ==========================================================

    st.divider()

    st.subheader("Trade Statistics")

    if ctx.statistics:

        st.json(ctx.statistics)

    else:

        st.info("Statistics not available.")