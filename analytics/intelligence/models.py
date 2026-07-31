from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# ============================================================
# Trade Intelligence Record
# ============================================================

@dataclass(slots=True)
class TradeIntelligenceRecord:
    """
    Complete market fingerprint captured for every
    trading decision.

    This object is designed for:

    • Historical validation
    • Similarity search
    • AI datasets
    • Strategy optimization
    • Performance analytics
    """

    # =====================================================
    # Metadata
    # =====================================================

    timestamp: datetime | None = None

    trading_day: str = ""

    expiry: str = ""

    session: str = ""

    # =====================================================
    # Market
    # =====================================================

    spot_price: float = 0.0

    atm_strike: float = 0.0

    futures_price: float = 0.0

    india_vix: float = 0.0

    # =====================================================
    # Option Chain
    # =====================================================

    strike: float = 0.0

    option_type: str = ""

    premium: float = 0.0

    implied_volatility: float = 0.0

    iv_rank: float = 0.0

    iv_percentile: float = 0.0

    open_interest: float = 0.0

    change_in_oi: float = 0.0

    volume: float = 0.0

    # =====================================================
    # Greeks
    # =====================================================

    delta: float = 0.0

    gamma: float = 0.0

    theta: float = 0.0

    vega: float = 0.0

    rho: float = 0.0

    # =====================================================
    # Dealer Positioning
    # =====================================================

    dealer_gamma: str = ""

    dealer_delta: str = ""

    gamma_exposure: float = 0.0

    delta_exposure: float = 0.0

    gamma_wall: float = 0.0

    gamma_flip: float = 0.0

    zero_gamma: float = 0.0

    # =====================================================
    # Market Structure
    # =====================================================

    trend: str = ""

    market_structure: str = ""

    institutional_bias: str = ""

    conviction: str = ""

    probability: float = 0.0

    # =====================================================
    # Technicals
    # =====================================================

    ad_ratio: float = 0.0

    pcr: float = 0.0

    rsi: float = 0.0

    atr: float = 0.0

    adx: float = 0.0

    vwap_distance: float = 0.0

    # =====================================================
    # Decision
    # =====================================================

    signal: str = ""

    confidence: float = 0.0

    trade_quality: float = 0.0

    strategy_name: str = ""

    execution_plan: str = ""

    reasons: List[str] = field(default_factory=list)

    # =====================================================
    # Trade
    # =====================================================

    entry_price: float = 0.0

    stop_loss: float = 0.0

    target1: float = 0.0

    target2: float = 0.0

    quantity: int = 0

    lots: int = 0

    risk_reward: float = 0.0

    # =====================================================
    # Exit
    # =====================================================

    exit_price: float = 0.0

    pnl: float = 0.0

    holding_minutes: float = 0.0

    exit_reason: str = ""

    outcome: str = ""

    # =====================================================
    # AI
    # =====================================================

    similarity_score: float = 0.0

    historical_win_rate: float = 0.0

    expected_move: float = 0.0

    expected_holding: float = 0.0

    expected_probability: float = 0.0