import streamlit as st

from app.services.live_service import LiveService

from app.components.institutional_signal import (
    show as institutional_signal
)

from app.components.institutional_summary import (
    show as institutional_summary
)

from app.components.dealer_analysis import (
    show as dealer_analysis
)

from app.components.gamma_analysis import (
    show as gamma_analysis
)

from app.components.probability_analysis import (
    show as probability_analysis
)

from app.components.volatility_analysis import (
    show as volatility_analysis
)

from app.components.liquidity_analysis import (
    show as liquidity_analysis
)

from app.components.open_interest_analysis import (
    show as open_interest_analysis
)


# ==========================================================
# PAGE
# ==========================================================

def show():

    service = LiveService()

    ctx = service.get_context()

    st.title("🏦 Institutional Dashboard")

    # ==========================================================
    # Institutional Trading Signal (Hero Banner)
    # ==========================================================

    institutional_signal(ctx)

    st.divider()

    # ==========================================================
    # Institutional Summary
    # ==========================================================

    institutional_summary(ctx)

    st.divider()

    # ==========================================================
    # Dealer Analysis
    # ==========================================================

    dealer_analysis(ctx)

    st.divider()

    # ==========================================================
    # Gamma Analysis
    # ==========================================================

    gamma_analysis(ctx)

    st.divider()

    # ==========================================================
    # Probability Analysis
    # ==========================================================

    probability_analysis(ctx)

    st.divider()

    # ==========================================================
    # Volatility Analysis
    # ==========================================================

    volatility_analysis(ctx)

    st.divider()

    # ==========================================================
    # Liquidity Analysis
    # ==========================================================

    liquidity_analysis(ctx)

    st.divider()

    # ==========================================================
    # Open Interest Analysis
    # ==========================================================

    open_interest_analysis(ctx)

    st.divider()

    # ==========================================================
    # Sprint Status
    # ==========================================================

    st.success(
        """
## ✅ Sprint 3 Completed

### Institutional Analytics

✔ Institutional Trading Signal

✔ Institutional Summary

✔ Dealer Analysis

✔ Gamma Analysis

✔ Probability Analysis

✔ Volatility Analysis

✔ Liquidity Analysis

✔ Open Interest Analysis

---

## 🚀 Sprint 4 Roadmap

✔ Strategy Dashboard

✔ Trade Setup Engine

✔ Entry / Exit Signal Engine

✔ Multi-Timeframe Confirmation

✔ Live Alerts

✔ Trade Journal

✔ Backtesting Engine

✔ Performance Analytics

---

**QuantNifty Institutional Dashboard is now fully operational.**
"""
    )