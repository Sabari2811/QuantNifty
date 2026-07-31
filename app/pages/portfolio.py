import streamlit as st

from app.services.live_service import LiveService


def show():
    """
    Portfolio Dashboard.
    """

    service = LiveService()
    ctx = service.get_context()

    portfolio = ctx.portfolio

    st.title("💼 Portfolio")

    if portfolio is None:
        st.info("Portfolio not available.")
        return

    # ==========================================================
    # ACCOUNT SUMMARY
    # ==========================================================

    st.subheader("Account Summary")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Available Cash", f"{portfolio.available_cash:.2f}")
    c2.metric("Invested", f"{portfolio.invested_amount:.2f}")
    c3.metric("Unrealized P&L", f"{portfolio.unrealized_pnl:.2f}")
    c4.metric("Realized P&L", f"{portfolio.realized_pnl:.2f}")

    st.divider()

    # ==========================================================
    # OPEN POSITIONS
    # ==========================================================

    st.subheader("Open Positions")

    if not portfolio.open_positions:
        st.info("No open positions.")
    else:

        rows = []

        for p in portfolio.open_positions:

            rows.append(
                {
                    "Signal": p.order.signal,
                    "Strike": p.order.strike,
                    "Type": p.order.option_type,
                    "Qty": p.order.quantity,
                    "Entry": p.order.entry_price,
                    "LTP": p.current_price,
                    "PnL": p.pnl,
                    "SL": p.stop_loss,
                    "Target": p.target,
                }
            )

        st.dataframe(rows, use_container_width=True)

    st.divider()

    # ==========================================================
    # CLOSED POSITIONS
    # ==========================================================

    st.subheader("Closed Positions")

    if not portfolio.closed_positions:
        st.info("No completed trades.")
    else:

        rows = []

        for p in portfolio.closed_positions:

            rows.append(
                {
                    "Signal": p.order.signal,
                    "Strike": p.order.strike,
                    "Type": p.order.option_type,
                    "Qty": p.order.quantity,
                    "Entry": p.order.entry_price,
                    "Exit": p.exit_price,
                    "PnL": p.pnl,
                }
            )

        st.dataframe(rows, use_container_width=True)