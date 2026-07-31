import streamlit as st
import plotly.graph_objects as go


def render(option_chain):
    """
    Open Interest Heatmap
    """

    st.subheader("📊 Open Interest Heatmap")

    if option_chain is None or option_chain.empty:
        st.warning("No Option Chain Data.")
        return

    df = option_chain.copy()

    fig = go.Figure()

    # -----------------------------
    # Call OI
    # -----------------------------

    fig.add_trace(

        go.Bar(

            x=df["Strike"],

            y=df["CE_OI"],

            name="Call OI",

            marker_color="green"

        )

    )

    # -----------------------------
    # Put OI
    # -----------------------------

    fig.add_trace(

        go.Bar(

            x=df["Strike"],

            y=df["PE_OI"],

            name="Put OI",

            marker_color="red"

        )

    )

    fig.update_layout(

        barmode="group",

        height=450,

        template="plotly_dark",

        title="Open Interest Distribution",

        xaxis_title="Strike",

        yaxis_title="Open Interest"

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )