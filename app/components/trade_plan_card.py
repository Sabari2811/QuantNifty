import streamlit as st

from decision.constants import Signal


def row(label, value):

    c1, c2 = st.columns([2, 2])

    with c1:
        st.write(f"**{label}**")

    with c2:
        st.write(value)


def show(ctx):

    decision = ctx.decision

    trade = decision.trade
    execution = trade.execution

    st.subheader("📋 Execution Plan")

    with st.container(border=True):

        # --------------------------------------------------
        # No Trade
        # --------------------------------------------------

        if decision.signal.name == Signal.WAIT.value:

            st.info("No trade generated for the current market conditions.")

            if decision.reasons:

                st.markdown("**Reasons**")

                for reason in decision.reasons:
                    st.write(f"• {reason}")

            return

        # --------------------------------------------------
        # Trade Details
        # --------------------------------------------------

        row("Strike", trade.strike)

        row("Option", trade.option_type)

        row("Premium Entry", execution.premium_entry)

        row("Stop Loss", execution.premium_stop_loss)

        row("Target 1", execution.premium_target1)

        row("Target 2", execution.premium_target2)

        row("Risk / Reward", execution.risk_reward)

        row("Trade Quality", execution.trade_quality)

        row("Lots", execution.lots)