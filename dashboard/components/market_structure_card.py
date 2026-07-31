import streamlit as st


def render(data):

    st.subheader("🏛 Market Structure")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Structure",
        data["structure"]
    )

    c2.metric(
        "Bias",
        data["bias"]
    )

    c3.metric(
        "Confidence",
        f'{data["confidence"]}%'
    )

    st.info(
        f'**Reason:** {data["reason"]}'
    )