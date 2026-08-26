import streamlit as st


def _acquisition_time(dashboard):
    """Return the latest canonical acquisition time used by this dashboard cycle."""
    provenance = getattr(dashboard, "data_provenance", None)
    acquisitions = (
        getattr(provenance, "spot", None),
        getattr(provenance, "option_chain", None),
        getattr(provenance, "candles", None),
    )
    timestamps = [
        item.acquired_at
        for item in acquisitions
        if item is not None and item.acquired_at is not None
    ]
    if not timestamps:
        return None
    return max(timestamps)


def render(dashboard):
    """
    QuantNifty Terminal Header
    """

    st.title("📈 QuantNifty Terminal")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Symbol", dashboard.symbol)
    c2.metric("Spot", f"{dashboard.spot:,.2f}")
    c3.metric("Expiry", dashboard.expiry)
    c4.metric("Provider", dashboard.provider.upper())

    session = "MOCK" if dashboard.provider.lower() == "mock" else "LIVE"
    c5.metric("Session", session)

    acquired_at = _acquisition_time(dashboard)
    updated = (
        acquired_at.astimezone().strftime("%H:%M:%S %Z")
        if acquired_at is not None
        else "UNAVAILABLE"
    )
    c6.metric("Acquired", updated)

    st.divider()
