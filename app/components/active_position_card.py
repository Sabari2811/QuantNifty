import streamlit as st

from datetime import datetime


def _holding_time(entry_time):

    if entry_time is None:
        return "--"

    delta = datetime.now() - entry_time

    total = int(delta.total_seconds())

    hours = total // 3600

    minutes = (total % 3600) // 60

    seconds = total % 60

    if hours:

        return f"{hours}h {minutes}m"

    return f"{minutes}m {seconds}s"


def active_position_card(ctx):

    st.subheader("💼 Active Position")

    position = ctx.position

    if position is None:

        st.info(

            "No active paper position.\n\n"

            "Waiting for the next institutional setup."

        )

        return

    order = position.order

    signal = order.signal

    badge = "🟢" if signal == "BUY_CALL" else "🔴"

    pnl = position.pnl

    contract = f"{order.strike} {order.option_type}"

    col1, col2 = st.columns([3, 1])

    with col1:

        st.markdown(

            f"### {badge} {signal.replace('_', ' ')}"

        )

        st.caption(contract)

    with col2:

        if position.closed:

            st.error("CLOSED")

        else:

            st.success("OPEN")

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "Entry",

            f"₹ {order.entry_price:.2f}"

        )

    with c2:

        st.metric(

            "Current",

            f"₹ {position.current_price:.2f}"

        )

    with c3:

        st.metric(

            "Quantity",

            order.quantity,

        )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(

            "Stop Loss",

            f"₹ {position.stop_loss:.2f}"

        )

    with c2:

        st.metric(

            "Target",

            f"₹ {position.target:.2f}"

        )

    with c3:

        st.metric(

            "Holding",

            _holding_time(

                order.order_time

            )

        )

    st.divider()

    if pnl >= 0:

        st.success(

            f"MTM Profit : ₹ {pnl:,.2f}"

        )

    else:

        st.error(

            f"MTM Loss : ₹ {pnl:,.2f}"

        )