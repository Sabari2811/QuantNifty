import streamlit as st


def render(score_data):
    institutional = score_data["institutional"]

    st.subheader("🏛 Institutional Score")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Score", f'{institutional["score"]}/100')
    c2.metric("Grade", institutional["grade"])
    c3.metric("Strength", institutional["strength"])
    c4.metric("Signal", institutional["signal"])

    st.progress(institutional["score"] / 100)

    reasons = institutional.get("reasons") or []
    if reasons:
        with st.expander(f"Reasons ({len(reasons)})", expanded=False):
            for reason in reasons:
                st.write("•", reason)
    else:
        st.caption("No institutional reasons available for this cycle.")
