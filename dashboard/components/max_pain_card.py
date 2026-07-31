import streamlit as st


def render(data):

    st.subheader("🎯 Max Pain")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Max Pain",
        f"{data['max_pain']:.0f}"
    )

    c2.metric(
        "Call OI",
        f"{data['call_oi']:,}"
    )

    c3.metric(
        "Put OI",
        f"{data['put_oi']:,}"
    )

    c4.metric(
        "Total OI",
        f"{data['total_oi']:,}"
    )

    st.caption(
        "Highest combined Open Interest strike"
    )