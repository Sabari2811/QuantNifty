import streamlit as st


def render(
    spot,
    dealer
):
    """
    Summary Cards
    """

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    # ======================================================
    # Spot
    # ======================================================

    with c1:

        st.metric(
            "Spot",
            f"{spot:.2f}"
        )

    # ======================================================
    # Dealer Gamma
    # ======================================================

    with c2:

        st.metric(
            "Dealer",
            dealer.dealer_gamma
        )

    # ======================================================
    # Gamma Flip
    # ======================================================

    with c3:

        st.metric(
            "Gamma Flip",
            str(
                dealer.gamma_flip
            )
        )

    # ======================================================
    # Gamma Wall
    # ======================================================

    with c4:

        st.metric(
            "Gamma Wall",
            str(
                dealer.gamma_wall
            )
        )

    # ======================================================
    # Market Mode
    # ======================================================

    with c5:

        st.metric(
            "Market",
            dealer.market_mode
        )

    # ======================================================
    # Expected Volatility
    # ======================================================

    with c6:

        st.metric(
            "Volatility",
            dealer.expected_volatility
        )

    st.divider()