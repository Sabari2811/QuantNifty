import streamlit as st
from datetime import datetime


def render(dashboard):
    """
    QuantNifty Terminal Header
    """

    st.title("📈 QuantNifty Terminal")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    # -----------------------------------
    # Symbol
    # -----------------------------------

    c1.metric(
        "Symbol",
        dashboard.symbol
    )

    # -----------------------------------
    # Spot
    # -----------------------------------

    c2.metric(
        "Spot",
        f"{dashboard.spot:,.2f}"
    )

    # -----------------------------------
    # Expiry
    # -----------------------------------

    c3.metric(
        "Expiry",
        dashboard.expiry
    )

    # -----------------------------------
    # Provider
    # -----------------------------------

    c4.metric(
        "Provider",
        dashboard.provider.upper()
    )

    # -----------------------------------
    # Session
    # -----------------------------------

    if dashboard.provider.lower() == "mock":

        session = "MOCK"

    else:

        session = "LIVE"

    c5.metric(
        "Session",
        session
    )

    # -----------------------------------
    # Last Refresh
    # -----------------------------------

    c6.metric(
        "Updated",
        datetime.now().strftime("%H:%M:%S")
    )

    st.divider()