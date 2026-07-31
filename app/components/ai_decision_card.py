import streamlit as st

from decision.constants import Signal


def show(ctx):

    decision = ctx.decision

    execution = decision.trade.execution

    st.subheader("🤖 AI Decision")

    with st.container(border=True):

        # --------------------------------------------------
        # Signal
        # --------------------------------------------------

        if decision.signal.name == Signal.BUY_CALL.value:

            st.success("🟢 BUY CALL")

        elif decision.signal.name == Signal.BUY_PUT.value:

            st.error("🔴 BUY PUT")

        else:

            st.warning("🟡 WAIT")

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = decision.signal.confidence

        st.write(f"Confidence : {confidence}%")

        st.progress(confidence / 100)

        st.divider()

        # --------------------------------------------------
        # Trade Quality
        # --------------------------------------------------

        if decision.signal.name == Signal.WAIT.value:

            st.metric(
                "Trade Quality",
                "--"
            )

        else:

            st.metric(
                "Trade Quality",
                execution.trade_quality
            )

        # --------------------------------------------------
        # Reasons
        # --------------------------------------------------

        st.write("Reasons")

        if decision.reasons:

            for reason in decision.reasons:

                st.write(f"• {reason}")

        else:

            st.write("No reasons available.")