import streamlit as st

from app.services.live_service import LiveService


def show():
    """
    Trade Journal.
    """

    service = LiveService()
    ctx = service.get_context()

    journal = ctx.journal

    st.title("📒 Trade Journal")

    if journal is None or not journal.records:
        st.info("No trades recorded.")
        return

    rows = []

    for trade in journal.records:

        rows.append(
            {
                "Entry Time": trade.entry_time,
                "Exit Time": trade.exit_time,
                "Signal": trade.signal,
                "Strategy": trade.strategy_name,
                "Strike": trade.strike,
                "Type": trade.option_type,
                "Qty": trade.quantity,
                "Entry": trade.entry_price,
                "Exit": trade.exit_price,
                "PnL": trade.pnl,
                "Reason": trade.exit_reason,
                "Confidence": trade.confidence,
                "Risk Reward": trade.risk_reward,
            }
        )

    st.dataframe(rows, use_container_width=True)