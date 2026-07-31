import streamlit as st
import plotly.graph_objects as go


def render(probability):
    """
    Bullish Probability Gauge
    """

    st.subheader("🎯 Bullish Probability")

    value = probability["bullish_probability"]

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=value,

            title={"text": "Bullish Probability"},

            gauge={

                "axis": {"range": [0, 100]},

                "bar": {"color": "green"},

                "steps": [

                    {"range": [0, 30], "color": "#ff4d4d"},

                    {"range": [30, 70], "color": "#ffcc00"},

                    {"range": [70, 100], "color": "#00cc66"}

                ]

            }

        )

    )

    fig.update_layout(

        template="plotly_dark",

        height=350

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )