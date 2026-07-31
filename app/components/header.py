import streamlit as st
from datetime import datetime


def show(ctx):

    left, center, right = st.columns([3, 2, 2])

    with left:

        st.title("📈 QuantNifty")

        st.caption(
            "Institutional Options Analytics Platform"
        )

    with center:

        st.metric(

            "NIFTY",

            round(ctx.spot, 2)

        )

    with right:

        st.metric(

            "Last Update",

            datetime.now().strftime("%H:%M:%S")

        )

    st.divider()