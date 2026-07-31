import streamlit as st

from app.theme.styles import CARD_STYLE


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(

    page_title="QuantNifty",

    page_icon="📈",

    layout="wide",

    initial_sidebar_state="expanded"

)

st.markdown(

    CARD_STYLE,

    unsafe_allow_html=True

)

# =====================================================
# IMPORT PAGES
# =====================================================

from app.pages.dashboard import show as dashboard
from app.pages.runtime import show as runtime
from app.pages.option_chain import show as option_chain
from app.pages.institutional import show as institutional

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(

    "Select",

    [

        "Dashboard",

        "Option Chain",

        "Institutional",

        "Strategy",

        "Runtime"

    ]

)

# =====================================================
# ROUTER
# =====================================================

if page == "Dashboard":

    dashboard()

elif page == "Option Chain":

     option_chain()

elif page == "Institutional":

    institutional()

elif page == "Strategy":

    st.header("🎯 Strategy")

    st.info("Coming Soon...")

elif page == "Runtime":

    runtime()