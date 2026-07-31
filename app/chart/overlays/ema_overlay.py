import plotly.graph_objects as go


class EMAOverlay:

    def render(

        self,

        fig,

        ctx

    ):

        candles = ctx.candles

        ema20 = candles["close"].ewm(

            span=20

        ).mean()

        fig.add_trace(

            go.Scatter(

                x=candles["datetime"],

                y=ema20,

                mode="lines",

                name="EMA 20"

            )

        )