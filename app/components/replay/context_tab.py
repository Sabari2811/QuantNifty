import streamlit as st


def show(ctx, session):

    st.subheader("Runtime Context")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Spot",
        f"{ctx.spot:,.2f}"
    )

    c2.metric(
        "Symbol",
        ctx.symbol
    )

    c3.metric(
        "Status",
        ctx.runtime_status
    )

    st.divider()

    a, b = st.columns(2)

    a.metric(
        "Replay Cycle",
        f"{session.index + 1}/{session.total}"
    )

    a.metric(
        "Recorded Cycle",
        ctx.cycle_no
    )

    b.metric(
        "Timestamp",
        ctx.timestamp
    )

    st.divider()

    st.json(
        {
            "Spot": ctx.spot,
            "Symbol": ctx.symbol,
            "Cycle": ctx.cycle_no,
            "Timestamp": ctx.timestamp,
            "Status": ctx.runtime_status
        }
    )