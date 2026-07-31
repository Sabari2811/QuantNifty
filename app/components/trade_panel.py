import streamlit as st


def show(ctx):

    analytics = ctx.analytics

    trade = analytics.get(
        "trade_plan",
        {}
    )

    st.subheader("Trade")

    signal = trade.get(
        "signal",
        "WAIT"
    )

    if signal == "BUY":

        st.success(signal)

    elif signal == "SELL":

        st.error(signal)

    else:

        st.warning(signal)

    st.write(
        f"Strike : {trade.get('recommended_strike', '-')}"
    )

    st.write(
        f"Entry : {trade.get('entry', '-')}"
    )

    st.write(
        f"SL : {trade.get('stop_loss', '-')}"
    )

    st.write(
        f"Target : {trade.get('target1', '-')}"
    )