import streamlit as st


def _metric(label, value):

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"**{label}**")

    with col2:
        st.markdown(str(value))


def _status(value):

    if value:
        return "🟢"

    return "🔴"


def show(ctx):

    st.subheader("🛡️ Risk Dashboard")

    if ctx is None:

        st.info("Runtime Context unavailable.")
        return

    risk = getattr(ctx, "risk_state", None)

    if risk is None:

        st.info("Risk Manager not initialized.")
        return

    portfolio = getattr(ctx, "portfolio", None)

    open_positions = 0

    if portfolio is not None:

        if hasattr(portfolio, "open_positions"):

            open_positions = len(portfolio.open_positions)

        elif hasattr(portfolio, "positions"):

            open_positions = len(portfolio.positions)

    trade_status = getattr(
        ctx,
        "trade_status",
        "-"
    )

    trade_block_reason = getattr(
        ctx,
        "trade_block_reason",
        "-"
    )

    with st.container(border=True):

        _metric(
            "Today's P&L",
            f"{risk.todays_pnl:.2f}"
        )

        _metric(
            "Trades Today",
            risk.trades_today
        )

        _metric(
            "Consecutive Losses",
            risk.consecutive_losses
        )

        _metric(
            "Open Positions",
            open_positions
        )

        cooldown = (
            risk.cooldown_until
            if risk.cooldown_until
            else "-"
        )

        _metric(
            "Cooldown",
            cooldown
        )

        _metric(
            "Trade Status",
            trade_status
        )

        _metric(
            "Block Reason",
            trade_block_reason
        )

        trading_allowed = (
            trade_status != "BLOCKED"
        )

        _metric(
            "Trading Allowed",
            _status(trading_allowed)
        )