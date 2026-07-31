import streamlit as st


def metric(label, value):

    c1, c2 = st.columns([2, 2])

    with c1:
        st.write(f"**{label}**")

    with c2:
        st.write(value)


def show(ctx):

    snapshot = ctx.snapshot

    if snapshot is None:

        st.warning("Market snapshot unavailable.")
        return

    dealer = snapshot.dealer
    expected = snapshot.expected_move
    max_pain = snapshot.max_pain

    st.subheader("🏦 Dealer Dashboard")

    with st.container(border=True):

        dealer_side = dealer.get(
            "dealer_gamma",
            "UNKNOWN"
        )

        if dealer_side == "LONG":
            dealer_display = "🟢 LONG"

        elif dealer_side == "SHORT":
            dealer_display = "🔴 SHORT"

        else:
            dealer_display = "🟡 UNKNOWN"

        metric(
            "Dealer Position",
            dealer_display
        )

        metric(
            "Spot",
            f"{snapshot.spot:,.2f}"
        )

        metric(
            "Gamma Flip",
            dealer.get(
                "gamma_flip",
                "-"
            )
        )

        metric(
            "Gamma Wall",
            dealer.get(
                "gamma_wall",
                "-"
            )
        )

        metric(
            "Call Wall",
            dealer.get(
                "call_wall",
                "-"
            )
        )

        metric(
            "Put Wall",
            dealer.get(
                "put_wall",
                "-"
            )
        )

        metric(
            "Max Pain",
            max_pain.get(
                "max_pain",
                "-"
            )
        )

        metric(
            "Expected Move",
            expected.get(
                "expected_move",
                "-"
            )
        )