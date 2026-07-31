import streamlit as st
import plotly.graph_objects as go
from app.chart.overlay_manager import OverlayManager

from app.chart.overlays.ema_overlay import EMAOverlay

def show(ctx):

    candles = ctx.candles

    if candles is None or candles.empty:

        st.warning("No candle data available.")

        return

    fig = go.Figure()

    manager = OverlayManager()

    manager.register(

        EMAOverlay()

    )

    fig.add_trace(

        go.Candlestick(

            x=candles["datetime"],

            open=candles["open"],

            high=candles["high"],

            low=candles["low"],

            close=candles["close"],

            name="NIFTY"

        )

    )

    fig.update_layout(

        title="NIFTY Live Candlestick",

        xaxis_title="Time",

        yaxis_title="Price",

        template="plotly_dark",

        height=650,

        xaxis_rangeslider_visible=False,

        margin=dict(

            l=20,

            r=20,

            t=50,

            b=20

        )

    )

    manager.render(

        fig,

        ctx

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )