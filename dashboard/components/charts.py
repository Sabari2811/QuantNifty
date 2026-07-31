import streamlit as st

from dashboard.charts.gamma_chart import build as gamma_chart
from dashboard.charts.iv_smile_chart import build as iv_chart
from dashboard.charts.dealer_heatmap import build as dealer_heatmap
from dashboard.charts.oi_profile_chart import build as oi_profile


def render(dashboard):
    """
    Analytics Charts Section
    """

    greeks = dashboard.greeks

    st.subheader("📊 Analytics Charts")

    # ======================================================
    # Row 1
    # ======================================================

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            gamma_chart(dashboard),
            use_container_width=True
        )

    with col2:

        st.plotly_chart(
            iv_chart(greeks),
            use_container_width=True
        )

    # ======================================================
    # Row 2
    # ======================================================

    col3, col4 = st.columns(2)

    with col3:

        st.plotly_chart(
            dealer_heatmap(greeks),
            use_container_width=True
        )

    with col4:

        st.plotly_chart(
            oi_profile(greeks),
            use_container_width=True
        )

    st.divider()