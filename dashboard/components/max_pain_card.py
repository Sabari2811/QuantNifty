import math

import streamlit as st


def _display(value, decimals=0):
    """Render a known numeric value or an explicit unknown marker."""
    if value is None:
        return "UNAVAILABLE"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    if math.isnan(numeric):
        return "UNAVAILABLE"
    if decimals == 0:
        return f"{numeric:,.0f}"
    return f"{numeric:,.{decimals}f}"


def render(data):
    """Render canonical max-pain values without fabricating missing fields."""

    values = data or {}

    st.subheader("🎯 Max Pain")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Max Pain", _display(values.get("max_pain")))
    c2.metric("Call OI", _display(values.get("call_oi")))
    c3.metric("Put OI", _display(values.get("put_oi")))
    c4.metric("Total OI", _display(values.get("total_oi")))

    st.caption("Highest combined Open Interest strike")
