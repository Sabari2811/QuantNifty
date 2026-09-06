import math

import streamlit as st


def _display(value, decimals=2):
    """Render a known numeric PCR value or an explicit unknown marker."""
    if value is None:
        return "UNAVAILABLE"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    if math.isnan(numeric):
        return "UNAVAILABLE"
    return f"{numeric:,.{decimals}f}"


def render(data):
    """Render canonical PCR values without fabricating missing data."""

    values = data or {}

    st.subheader("📊 Put Call Ratio")

    c1, c2, c3 = st.columns(3)

    c1.metric("OI PCR", _display(values.get("oi_pcr")))
    c2.metric("Volume PCR", _display(values.get("volume_pcr")))
    c3.metric(
        "Sentiment",
        values.get("sentiment") if values.get("sentiment") is not None else "UNAVAILABLE",
    )
