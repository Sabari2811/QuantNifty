import os
import sys

# ==========================================================
# PROJECT ROOT
# ==========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ==========================================================
# IMPORTS
# ==========================================================

import streamlit as st

from config.settings import PROVIDER
from dashboard.dashboard_controller import DashboardController
from dashboard.components import institutional_score_card

from dashboard.components import (

    header,

    market_banner,

    market_regime,

    runtime_card,

    signal_card,

    probability_gauge,

    expected_move_card,

    max_pain_card,

    pcr_card,

    dealer_card,

    dealer_flow_card,

    market_structure_card,

    liquidity_card,

    trade_plan,

    risk_card,

    gamma_heatmap,

    oi_heatmap,

    option_chain,

    greeks_table,

    charts

)

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(

    page_title="QuantNifty Terminal",

    page_icon="📈",

    layout="wide"

)

# ==========================================================
# CONTROLLER
# ==========================================================

@st.cache_resource
def get_controller():

    return DashboardController()

controller = get_controller()

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("⚙ QuantNifty")

    st.success(

        f"Provider : {PROVIDER.upper()}"

    )

    symbol = st.selectbox(

        "Index",

        [

            "NIFTY",

            "BANKNIFTY",

            "FINNIFTY"

        ]

    )

    levels = st.slider(

        "Strike Levels",

        min_value=2,

        max_value=10,

        value=5

    )

# ==========================================================
# LOAD
# ==========================================================

try:

    dashboard = controller.load(

        symbol,

        levels

    )

except Exception as e:

    st.exception(e)

    st.stop()

# ==========================================================
# HEADER
# ==========================================================

header.render(dashboard)

market_banner.render(dashboard)

market_regime.render(dashboard)

runtime_card.render(dashboard)

# ==========================================================
# SIGNAL
# ==========================================================

signal_card.render(

    dashboard.probability,

    dashboard.dealer

)

institutional_score_card.render(
    dashboard.institutional_score
)

probability_gauge.render(

    dashboard.probability

)

# ==========================================================
# INSTITUTIONAL ANALYTICS
# ==========================================================

expected_move_card.render(

    dashboard.expected_move

)

max_pain_card.render(

    dashboard.max_pain

)

pcr_card.render(

    dashboard.pcr

)

market_structure_card.render(

    dashboard.market_structure

)

# ==========================================================
# DEALER ANALYTICS
# ==========================================================

dealer_card.render(

    dashboard.dealer

)

dealer_flow_card.render(

    dashboard.dealer_flow

)

# ==========================================================
# LIQUIDITY
# ==========================================================

liquidity_card.render(

    dashboard.liquidity

)

# ==========================================================
# TRADE PLAN
# ==========================================================

trade_plan.render(

    dashboard.trade_plan,

    dashboard.signal

)

# ==========================================================
# RISK
# ==========================================================

risk_card.render(

    dashboard.risk

)

# ==========================================================
# HEATMAPS
# ==========================================================

gamma_heatmap.render(

    dashboard.greeks

)

oi_heatmap.render(

    dashboard.option_chain

)

# ==========================================================
# OPTION CHAIN
# ==========================================================

option_chain.render(

    dashboard.option_chain

)

# ==========================================================
# LIVE GREEKS
# ==========================================================

greeks_table.render(

    dashboard.greeks

)

# ==========================================================
# CHARTS
# ==========================================================

charts.render(

    dashboard

)

# ==========================================================
# RAW ANALYTICS
# ==========================================================

with st.expander("📦 Analytics Output"):

    st.json(

        dashboard.analytics

    )