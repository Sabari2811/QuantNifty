import streamlit as st

from runtime.market_clock import MarketClock


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


def _format_acquisition_time(acquired_at):
    if acquired_at is None:
        return "UNAVAILABLE"
    if isinstance(acquired_at, str):
        try:
            from datetime import datetime
            acquired_at = datetime.fromisoformat(acquired_at.replace("Z", "+00:00"))
        except ValueError:
            return str(acquired_at)
    return acquired_at.astimezone().strftime("%H:%M:%S %Z")


def render(dashboard):
    """Render the QuantNifty terminal identity and unambiguous session state."""
    st.title("📈 QuantNifty Terminal")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Symbol", dashboard.symbol)
    c2.metric("Spot", f"{dashboard.spot:,.2f}")
    c3.metric("Expiry", dashboard.expiry)
    c4.metric("Provider", dashboard.provider.upper())

    market_status = MarketClock().market_status()
    c5.metric("Market Session", market_status)

    acquired_at = _acquisition_time(dashboard)
    c6.metric("Acquired", _format_acquisition_time(acquired_at))

    st.caption(
        "Market Session reflects NSE trading hours. Acquired is the client-side "
        "receipt time; provider quote timestamps are shown separately in data quality."
    )
    st.divider()
