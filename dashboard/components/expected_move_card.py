import math

import streamlit as st


def _display(value, suffix=""):
    """Render a known value or an explicit unknown marker."""
    if value is None:
        return "UNAVAILABLE"
    return f"{value}{suffix}"


def _display_number(value, decimals=2, prefix=""):
    """Render a finite number or an explicit unknown marker."""
    if value is None:
        return "UNAVAILABLE"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    if not math.isfinite(numeric):
        return "UNAVAILABLE"
    return f"{prefix}{numeric:,.{decimals}f}"


def render(expected_move):
    """Render canonical expected-move values without inventing missing data."""

    data = expected_move or {}
    spot = data.get("spot")
    move = data.get("expected_move")
    upper = data.get("upper")
    lower = data.get("lower")
    method = data.get("method")

    st.subheader("📈 Expected Move")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Spot", _display_number(spot))
    c2.metric("Expected Move", _display_number(move, prefix="± "))
    c3.metric("Upper", _display_number(upper))
    c4.metric("Lower", _display_number(lower))

    st.caption(f"Calculation Method : {_display(method)}")
