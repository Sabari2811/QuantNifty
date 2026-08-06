import streamlit as st


def show(ctx):

    st.error("NEW DECISION TAB LOADED")

    st.text(f"TYPE = {type(ctx.decision)}")

    st.text(f"IS NONE = {ctx.decision is None}")

    st.write("VALUE BELOW")

    st.code(repr(ctx.decision))

    st.write("CTX TYPE")

    st.code(repr(ctx))