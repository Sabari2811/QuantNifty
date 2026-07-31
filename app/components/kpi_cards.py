import streamlit as st

from decision.constants import Signal


def show(ctx):

    snapshot = ctx.snapshot
    portfolio = ctx.portfolio
    decision = ctx.decision

    # ----------------------------------------------------------
    # Safe defaults
    # ----------------------------------------------------------

    dealer_gamma = "-"

    trade_quality = "--"

    risk_reward = "--"

    # ----------------------------------------------------------
    # Snapshot
    # ----------------------------------------------------------

    if snapshot is not None:

        dealer = snapshot.dealer

        if dealer is not None:

            dealer_gamma = dealer.get(
                "dealer_gamma",
                "-"
            )

    # ----------------------------------------------------------
    # Decision
    # ----------------------------------------------------------

    if (
        decision is not None
        and decision.signal.name != Signal.WAIT.value
        and decision.trade is not None
        and decision.trade.execution is not None
    ):

        execution = decision.trade.execution

        if execution.trade_quality not in (None, 0):
            trade_quality = execution.trade_quality

        if execution.risk_reward not in (None, 0):
            risk_reward = execution.risk_reward

    # ==========================================================
    # ROW 1 - MARKET KPIs
    # ==========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        spot = 0

        if snapshot is not None:
            spot = snapshot.spot

        st.metric(
            "Spot",
            f"{spot:,.2f}"
        )

    with col2:

        st.metric(
            "Dealer",
            dealer_gamma
        )

    with col3:

        st.metric(
            "Trade Quality",
            trade_quality
        )

    with col4:

        st.metric(
            "Risk / Reward",
            risk_reward
        )

    st.divider()

    # ==========================================================
    # ROW 2 - PAPER TRADING KPIs
    # ==========================================================

    if portfolio is not None:

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Available Cash",
                f"₹{portfolio.available_cash:,.2f}"
            )

        with col2:

            st.metric(
                "Invested",
                f"₹{portfolio.invested_amount:,.2f}"
            )

        with col3:

            st.metric(
                "Realized P&L",
                f"₹{portfolio.realized_pnl:,.2f}"
            )

        with col4:

            st.metric(
                "Unrealized P&L",
                f"₹{portfolio.unrealized_pnl:,.2f}"
            )

        st.divider()