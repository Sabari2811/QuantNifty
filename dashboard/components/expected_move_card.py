import streamlit as st


def render(expected_move):

    st.subheader("📈 Expected Move")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Spot",
        f"{expected_move['spot']:.2f}"
    )

    c2.metric(
        "Expected Move",
        f"± {expected_move['expected_move']:.2f}"
    )

    c3.metric(
        "Upper",
        f"{expected_move['upper']:.2f}"
    )

    c4.metric(
        "Lower",
        f"{expected_move['lower']:.2f}"
    )

    st.caption(
        f"Calculation Method : {expected_move['method']}"
    )