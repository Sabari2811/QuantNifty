import streamlit as st


def render(score_data):

    institutional = score_data["institutional"]

    st.subheader("🏛 Institutional Score")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Score",
        f'{institutional["score"]}/100'
    )

    c2.metric(
        "Grade",
        institutional["grade"]
    )

    c3.metric(
        "Strength",
        institutional["strength"]
    )

    c4.metric(
        "Signal",
        institutional["signal"]
    )

    st.progress(
        institutional["score"] / 100
    )

    st.write("Reasons")

    for r in institutional["reasons"]:

        st.write("•", r)