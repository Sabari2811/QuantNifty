import streamlit as st


def render(risk):

    st.subheader("🛡 Risk Management")

    if not risk:

        st.info("Risk data unavailable.")

        return

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Capital Per Trade",
                risk.get("capital_per_trade", "-")
            )

            st.metric(
                "Capital Utilization",
                risk.get("capital_utilization", "-")
            )

            st.metric(
                "Max Daily Loss",
                risk.get("max_daily_loss", "-")
            )

        with col2:

            st.metric(
                "Max Open Positions",
                risk.get("max_open_positions", "-")
            )

            st.metric(
                "Cooldown",
                risk.get("cooldown", "-")
            )

            st.metric(
                "Consecutive Loss Limit",
                risk.get("loss_limit", "-")
            )