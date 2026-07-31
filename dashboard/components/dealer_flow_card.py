import streamlit as st


def render(data):

    st.subheader("🏦 Dealer Flow")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Dealer Delta",
        data["dealer_delta"]
    )

    c2.metric(
        "Dealer Vanna",
        data["dealer_vanna"]
    )

    c3.metric(
        "Dealer Charm",
        data["dealer_charm"]
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Pressure",
        data["dealer_pressure"]
    )

    c2.metric(
        "Hedging",
        data["dealer_hedging"]
    )

    c3.metric(
        "Flip Probability",
        f'{data["flip_probability"]}%'
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total DEX",
        f'{data["total_dex"]:,.0f}'
    )

    c2.metric(
        "Total Vanna",
        f'{data["total_vanna"]:,.0f}'
    )

    c3.metric(
        "Total Charm",
        f'{data["total_charm"]:,.0f}'
    )