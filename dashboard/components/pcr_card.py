import streamlit as st


def render(data):

    st.subheader("📊 Put Call Ratio")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "OI PCR",
        f"{data['oi_pcr']:.2f}"
    )

    c2.metric(
        "Volume PCR",
        f"{data['volume_pcr']:.2f}"
    )

    c3.metric(
        "Sentiment",
        data["sentiment"]
    )