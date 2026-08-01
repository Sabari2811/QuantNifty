import streamlit as st

from app.services.live_service import LiveService
from runtime.runtime_mode import RuntimeMode


def show():

    service = LiveService()

    st.title("⚙ Runtime")

    # ==========================================================
    # Runtime Mode
    # ==========================================================

    st.subheader("Runtime Mode")

    mode = st.selectbox(

        "Mode",

        [

            RuntimeMode.LIVE,

            RuntimeMode.REPLAY_FAST,

            RuntimeMode.REPLAY_RECOMPUTE,

        ],

        format_func=lambda x: x.value,

    )

    st.divider()

    # ==========================================================
    # Runtime Controls
    # ==========================================================

    st.subheader("Runtime")

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "▶ Start Runtime",
            use_container_width=True,
        ):

            service.start()

    with c2:

        if st.button(
            "■ Stop Runtime",
            use_container_width=True,
        ):

            service.stop()

    st.divider()

    # ==========================================================
    # Replay Controls
    # ==========================================================

    if mode != RuntimeMode.LIVE:

        st.subheader("Replay Controls")

        r1, r2, r3, r4 = st.columns(4)

        with r1:

            st.button(
                "⏮ Previous",
                use_container_width=True,
                disabled=True,
            )

        with r2:

            st.button(
                "▶ Play",
                use_container_width=True,
                disabled=True,
            )

        with r3:

            st.button(
                "⏸ Pause",
                use_container_width=True,
                disabled=True,
            )

        with r4:

            st.button(
                "⏭ Next",
                use_container_width=True,
                disabled=True,
            )

        speed = st.select_slider(

            "Replay Speed",

            options=[1, 2, 5, 10, 25, 50],

            value=1,

            disabled=True,

        )

        st.progress(0)

        st.caption("Replay integration coming in Sprint 2.")

        st.divider()

    # ==========================================================
    # Context
    # ==========================================================

    ctx = service.get_context()

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

    st.divider()

    st.subheader("Open Position")

    if ctx.position is None:

        st.info("No active position.")

    else:

        st.json(vars(ctx.position))

    st.divider()

    st.subheader("Last Completed Trade")

    if ctx.last_trade is None:

        st.info("No completed trades.")

    else:

        st.json(vars(ctx.last_trade))

    st.divider()

    st.subheader("Trade Statistics")

    if ctx.statistics:

        st.json(ctx.statistics)

    else:

        st.info("Statistics not available.")