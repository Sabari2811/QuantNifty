import streamlit as st


def _price(value):

    if value is None:
        return "-"

    if isinstance(value, (int, float)):
        return f"{value:,.2f}"

    return str(value)


def _row(icon, title, value):

    left, right = st.columns([3, 1])

    with left:
        st.markdown(f"{icon} **{title}**")

    with right:
        st.markdown(f"**{_price(value)}**")


def show(ctx):

    st.subheader("🗺️ Dealer Market Map")

    snapshot = ctx.snapshot

    if snapshot is None:

        with st.container(border=True):
            st.info("⏳ Waiting for first market cycle...")

        return

    dealer = snapshot.dealer
    max_pain = snapshot.max_pain
    expected = snapshot.expected_move

    dealer_side = dealer.get("dealer_gamma", "UNKNOWN")

    if dealer_side == "LONG":
        dealer_display = "🟢 LONG"
        interpretation = (
            "Dealers are net LONG. Positive gamma markets "
            "often produce lower volatility and mean reversion."
        )

    elif dealer_side == "SHORT":
        dealer_display = "🔴 SHORT"
        interpretation = (
            "Dealers are net SHORT. Negative gamma markets "
            "can expand volatility and trend strongly."
        )

    else:
        dealer_display = "🟡 UNKNOWN"
        interpretation = "Dealer positioning is unavailable."

    with st.container(border=True):

        _row(
            "🏦",
            "Dealer Position",
            dealer_display
        )

        _row(
            "⭐",
            "Spot",
            snapshot.spot
        )

        _row(
            "🟣",
            "Gamma Flip",
            dealer.get("gamma_flip")
        )

        _row(
            "🟠",
            "Gamma Wall",
            dealer.get("gamma_wall")
        )

        _row(
            "🟢",
            "Put Wall",
            dealer.get("put_wall")
        )

        _row(
            "🔴",
            "Call Wall",
            dealer.get("call_wall")
        )

        _row(
            "🟡",
            "Max Pain",
            max_pain.get("max_pain")
        )

        _row(
            "📈",
            "Expected Move",
            expected.get("expected_move")
        )

        st.divider()

        st.markdown("**Market Interpretation**")
        st.info(interpretation)