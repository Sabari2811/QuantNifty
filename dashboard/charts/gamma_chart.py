import plotly.graph_objects as go


def build(dashboard):
    """
    Professional Gamma Exposure Chart
    """

    greeks = dashboard.greeks
    dealer = dashboard.dealer

    colors = []

    for value in greeks["NET_GEX"]:

        if value >= 0:
            colors.append("#00CC66")      # Green

        else:
            colors.append("#FF4D4D")      # Red

    fig = go.Figure()

    fig.add_bar(

        x=greeks["Strike"],

        y=greeks["NET_GEX"],

        marker_color=colors,

        customdata=greeks[["CE_GEX", "PE_GEX"]].values,

        hovertemplate=
        "<b>Strike</b>: %{x}<br>" +
        "NET GEX : %{y:.2f}<br>" +
        "CE GEX : %{customdata[0]:.2f}<br>" +
        "PE GEX : %{customdata[1]:.2f}<extra></extra>"

    )

    # =====================================================
    # Zero Line
    # =====================================================

    fig.add_hline(

        y=0,

        line_dash="dot",

        line_color="gray"

    )

    # =====================================================
    # Spot Price
    # =====================================================

    fig.add_vline(

        x=dashboard.spot,

        line_color="white",

        line_width=2,

        line_dash="dash",

        annotation_text="Spot"

    )

    # =====================================================
    # Gamma Flip
    # =====================================================

    if dealer.gamma_flip is not None:

        fig.add_vline(

            x=dealer.gamma_flip,

            line_color="red",

            line_width=2,

            annotation_text="Gamma Flip"

        )

    # =====================================================
    # Gamma Wall
    # =====================================================

    if dealer.gamma_wall is not None:

        fig.add_vline(

            x=dealer.gamma_wall,

            line_color="green",

            line_width=2,

            annotation_text="Gamma Wall"

        )

    fig.update_layout(

        title="Gamma Exposure",

        xaxis_title="Strike",

        yaxis_title="NET GEX",

        template="plotly_dark",

        height=500,

        showlegend=False

    )

    return fig