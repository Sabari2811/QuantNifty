import plotly.graph_objects as go


def build(greeks):
    """
    Dealer Gamma Heatmap
    """

    colors = []

    for value in greeks["NET_GEX"]:

        if value > 100:

            colors.append("green")

        elif value < -100:

            colors.append("red")

        else:

            colors.append("gray")

    fig = go.Figure()

    fig.add_bar(

        x=greeks["Strike"],

        y=greeks["NET_GEX"],

        marker_color=colors,

        text=[round(v, 1) for v in greeks["NET_GEX"]],

        textposition="outside"

    )

    fig.update_layout(

        title="Dealer Gamma Heatmap",

        xaxis_title="Strike",

        yaxis_title="NET GEX",

        template="plotly_dark",

        height=450,

        showlegend=False

    )

    return fig