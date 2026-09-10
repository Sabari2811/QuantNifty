"""Presentation of persisted paper-trade performance and adaptive-brain state."""
from __future__ import annotations

from datetime import datetime, timezone
import math

import pandas as pd
import streamlit as st

from brain.adaptive_brain import AdaptiveBrain
from paper_trading.broker import PaperBroker


def _money(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "UNAVAILABLE"
    return f"₹{value:,.2f}" if math.isfinite(value) else "UNAVAILABLE"


def _brain_stats(brain):
    records = brain.store.records()
    resolved = [r for r in records if r.get("outcome") in {"WIN", "LOSS"}]
    wins = sum(r.get("outcome") == "WIN" for r in resolved)
    return {
        "observations": len(records),
        "resolved": len(resolved),
        "wins": wins,
        "losses": len(resolved) - wins,
        "win_rate": (wins * 100.0 / len(resolved)) if resolved else 0.0,
        "last_learning": records[-1].get("timestamp") if records else None,
    }


def _today_pnl(trades):
    today = datetime.now(timezone.utc).date()
    total = 0.0
    for trade in trades:
        exit_time = getattr(trade, "exit_time", None)
        if exit_time is None:
            continue
        if getattr(exit_time, "tzinfo", None) is None:
            exit_date = exit_time.date()
        else:
            exit_date = exit_time.astimezone(timezone.utc).date()
        if exit_date == today:
            total += float(trade.pnl)
    return total


def _decision_rows(records):
    rows = []
    for record in records:
        timestamp = record.get("timestamp")
        outcome = record.get("outcome") or "PENDING"
        rows.append({
            "Time": timestamp,
            "Cycle": record.get("cycle_no", 0),
            "Decision": record.get("signal", ""),
            "Outcome": outcome,
            "Historical Win Rate": record.get("historical_win_rate", 0.0),
            "Similarity": record.get("similarity_score", 0.0),
            "Trade ID": record.get("trade_id", ""),
            "Duplicate": "YES" if record.get("duplicate_outcome") else "",
        })
    return rows


def render():
    """Render the paper-trading ledger and incremental Brain telemetry."""
    broker = PaperBroker()
    trades = broker.journal.all_trades()
    summary = broker.journal.summary()
    brain = AdaptiveBrain()
    brain_stats = _brain_stats(brain)

    st.subheader("🧠 AI Brain & Paper Performance")
    with st.container(border=True):
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Today's P&L", _money(_today_pnl(trades)))
        c2.metric("Total P&L", _money(summary["total_pnl"]))
        c3.metric("Paper Trades", summary["total_trades"])
        c4.metric("Win Rate", f"{summary['win_rate']:.2f}%")
        c5.metric("Max Drawdown", _money(getattr(broker.performance, "max_drawdown", 0.0)))

        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Brain Observations", brain_stats["observations"])
        b2.metric("Resolved Outcomes", brain_stats["resolved"])
        b3.metric("Learned Wins / Losses", f"{brain_stats['wins']} / {brain_stats['losses']}")
        b4.metric("Historical Outcome Rate", f"{brain_stats['win_rate']:.2f}%")

        if brain_stats["last_learning"]:
            st.caption(f"Last brain observation: {brain_stats['last_learning']}")
        else:
            st.caption("No persisted brain observations yet.")

    records = brain.store.records()
    if records:
        st.markdown("#### Brain Decision Ledger")
        st.dataframe(
            pd.DataFrame(_decision_rows(records[-100:])).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

    if trades:
        rows = []
        cumulative = 0.0
        for trade in sorted(trades, key=lambda t: t.exit_time):
            cumulative += float(trade.pnl)
            rows.append({
                "Exit": trade.exit_time,
                "Signal": trade.signal,
                "Type": trade.option_type,
                "Strike": trade.strike,
                "Qty": trade.quantity,
                "Entry": trade.entry_price,
                "Exit Price": trade.exit_price,
                "P&L": trade.pnl,
                "Cumulative P&L": cumulative,
                "Reason": trade.exit_reason,
                "Strategy": trade.strategy_name,
            })
        st.markdown("#### Paper Trade Journal")
        st.dataframe(pd.DataFrame(rows).sort_values("Exit", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No completed paper trades are persisted yet. WAIT decisions and unresolved observations remain visible in the Brain Decision Ledger.")

    st.markdown("#### Brain learning state")
    st.write(
        "The Brain observes canonical market/decision fingerprints, persists them, and learns only from resolved paper/live outcomes. "
        "Resolved trades are deduplicated by paper order ID so repeated market cycles cannot teach the same trade multiple times. "
        "It restores its history after restart. Decision mutation remains disabled during validation until adaptive behavior is separately certified."
    )
