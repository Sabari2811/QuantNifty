import streamlit as st


def render(greeks):

    st.subheader("🧮 Live Greeks")

    st.dataframe(
        greeks,
        use_container_width=True,
        height=340
    )

    st.divider()