import streamlit as st


def trade_journal_card(ctx):
    """
    Displays the most recent completed paper trades.
    """

    st.subheader("📜 Recent Trades")

    journal = getattr(ctx, "journal", None)

    if journal is None:
        st.info("Trade journal not available.")
        return

    trades = journal.recent_trades(10)

    if not trades:
        st.info(
            "No completed trades yet.\n\n"
            "Completed paper trades will appear here."
        )
        return

    rows = []

    for trade in trades:

        signal = (
            "🟢 BUY CALL"
            if trade.signal == "BUY_CALL"
            else "🔴 BUY PUT"
        )

        pnl = (
            f"+₹{trade.pnl:,.2f}"
            if trade.pnl >= 0
            else f"-₹{abs(trade.pnl):,.2f}"
        )

        rows.append(
            {
                "Time": trade.exit_time.strftime("%H:%M"),
                "Signal": signal,
                "Contract": f"{trade.strike} {trade.option_type}",
                "Entry": round(trade.entry_price, 2),
                "Exit": round(trade.exit_price, 2),
                "P&L": pnl,
                "Reason": trade.exit_reason,
            }
        )

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )