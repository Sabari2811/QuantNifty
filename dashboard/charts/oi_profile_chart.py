import plotly.graph_objects as go


def build(greeks):
    """
    Open Interest Profile
    """

    fig = go.Figure()

    # Call OI
    fig.add_bar(

        x=greeks["Strike"],

        y=greeks["CE_OI"],

        name="Call OI",

        marker_color="#ff4d4d"

    )

    # Put OI
    fig.add_bar(

        x=greeks["Strike"],

        y=greeks["PE_OI"],

        name="Put OI",

        marker_color="#00cc66"

    )

    fig.update_layout(

        title="Open Interest Profile",

        xaxis_title="Strike",

        yaxis_title="Open Interest",

        barmode="group",

        template="plotly_dark",

        height=450

    )

    return fig