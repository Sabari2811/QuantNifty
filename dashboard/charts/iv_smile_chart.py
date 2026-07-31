import plotly.graph_objects as go


def build(greeks):

    fig = go.Figure()

    fig.add_scatter(

        x=greeks["Strike"],

        y=greeks["CE_IV"],

        mode="lines+markers",

        name="Call IV"

    )

    fig.add_scatter(

        x=greeks["Strike"],

        y=greeks["PE_IV"],

        mode="lines+markers",

        name="Put IV"

    )

    fig.update_layout(

        title="IV Smile",

        xaxis_title="Strike",

        yaxis_title="Implied Volatility",

        template="plotly_dark",

        height=450

    )

    return fig