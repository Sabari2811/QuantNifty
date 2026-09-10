import math

import streamlit as st


def _status_icon(status: str):
    if not status:
        return "⚪"
    status = str(status).upper()
    if status in ("RUNNING", "EXECUTED"):
        return "🟢"
    if status in ("READY", "IDLE"):
        return "🟡"
    if status == "BLOCKED":
        return "🔴"
    if status == "ERROR":
        return "❌"
    return "⚪"


def _display(value, missing="UNAVAILABLE"):
    if value is None:
        return missing
    if isinstance(value, float) and not math.isfinite(value):
        return missing
    return value


def _metric(label, value):
    col1, col2 = st.columns([2, 3])
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        st.write(value)


def render(dashboard):
    st.subheader("⚙ Runtime")
    with st.container(border=True):
        runtime_status = _display(dashboard.runtime_status)
        runtime = f"{_status_icon(runtime_status)} {runtime_status}"

        trade_status = _display(dashboard.trade_status)
        trade = f"{_status_icon(trade_status)} {trade_status}"

        # `position` is a canonical position object (or None), not a boolean.
        # Preserve the semantic meaning at the UI boundary: object => open,
        # None => no open position, without coercing the object to a bool.
        position = "YES" if dashboard.position is not None else "NO"
        last_trade = "AVAILABLE" if dashboard.last_trade is not None else "UNAVAILABLE"

        _metric("Runtime", runtime)
        _metric("Cycle", _display(dashboard.cycle_no))
        _metric("Trade Status", trade)
        _metric("Block Reason", _display(dashboard.trade_block_reason))
        _metric("Open Position", position)
        _metric("Last Trade", last_trade)
