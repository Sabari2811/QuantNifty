import streamlit as st


def show(ctx):

    st.subheader("Analytics")

    analytics = ctx.analytics

    if analytics is None:

        st.info("No analytics available.")

        return

    st.write("Analytics Type")

    st.write(type(analytics))

    st.divider()

    st.write("Analytics Data")

    st.write(analytics)