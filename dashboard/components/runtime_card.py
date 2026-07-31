import streamlit as st


def _status_icon(status: str):

    if not status:
        return "⚪"

    status = status.upper()

    if status in ("RUNNING", "EXECUTED"):
        return "🟢"

    if status in ("READY", "IDLE"):
        return "🟡"

    if status == "BLOCKED":
        return "🔴"

    if status == "ERROR":
        return "❌"

    return "⚪"


def _metric(label, value):

    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(f"**{label}**")

    with col2:
        st.write(value)


def render(dashboard):

    st.subheader("⚙ Runtime")

    with st.container(border=True):

        runtime = (
            f"{_status_icon(dashboard.runtime_status)} "
            f"{dashboard.runtime_status}"
        )

        trade = (
            f"{_status_icon(dashboard.trade_status)} "
            f"{dashboard.trade_status or '-'}"
        )

        position = "YES" if dashboard.position else "NO"

        last_trade = (
            "AVAILABLE"
            if dashboard.last_trade
            else "-"
        )

        _metric(
            "Runtime",
            runtime
        )

        _metric(
            "Cycle",
            dashboard.cycle_no
        )

        _metric(
            "Trade Status",
            trade
        )

        _metric(
            "Block Reason",
            dashboard.trade_block_reason or "-"
        )

        _metric(
            "Open Position",
            position
        )

        _metric(
            "Last Trade",
            last_trade
        )