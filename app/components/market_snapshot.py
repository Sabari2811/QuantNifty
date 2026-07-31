import streamlit as st


def show(ctx):

    analytics = ctx.analytics

    dealer = analytics.get("dealer", {})
    expected = analytics.get("expected_move", {})
    pcr = analytics.get("pcr", {})
    max_pain = analytics.get("max_pain", {})

    st.subheader("Market Snapshot")

    st.write(
        f"Expected Move : {expected.get('expected_move', '-')}"
    )

    st.write(
        f"PCR : {pcr.get('oi_pcr', '-')}"
    )

    st.write(
        f"Max Pain : {max_pain.get('max_pain', '-')}"
    )

    st.write(
        f"Gamma Flip : {dealer.get('gamma_flip', '-')}"
    )

    st.write(
        f"Gamma Wall : {dealer.get('gamma_wall', '-')}"
    )