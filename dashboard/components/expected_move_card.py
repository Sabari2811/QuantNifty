import streamlit as st


def _display(value, suffix=""):
    return "UNAVAILABLE" if value is None else f"{value}{suffix}"


def _display_number(value, decimals=2, prefix=""):
    return "UNAVAILABLE" if value is None else f"{prefix}{value:,.{decimals}f}"


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

    st.caption(
        f"Calculation Method : {_display(method)}"
    )
