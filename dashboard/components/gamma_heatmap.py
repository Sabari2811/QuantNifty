import streamlit as st
import plotly.express as px


def render(greeks_df):
    """
    Live Gamma Exposure Heatmap
    """

    st.subheader("📊 Gamma Exposure Heatmap")

    if greeks_df is None or greeks_df.empty:
        st.warning("No Gamma data available.")
        return

    df = greeks_df.copy()

    if "NET_GEX" not in df.columns:
        st.warning("NET_GEX column not found.")
        return

    fig = px.bar(
        df,
        x="Strike",
        y="NET_GEX",
        color="NET_GEX",
        color_continuous_scale="RdYlGn",
        title="Net Gamma Exposure by Strike"
    )

    fig.update_layout(
        height=450,
        xaxis_title="Strike",
        yaxis_title="NET GEX",
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )