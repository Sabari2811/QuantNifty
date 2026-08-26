"""Canonical backend -> dashboard mapping for decision fields."""


def adapt_decision(dashboard) -> dict:
    """Expose decision fields from one DashboardData cycle without recomputation."""
    signal = dashboard.signal or {}
    probability = dashboard.probability or {}
    trade_plan = dashboard.trade_plan or {}

    return {
        "signal": signal.get("signal"),
        "bullish_probability": probability.get("bullish_probability"),
        "bearish_probability": probability.get("bearish_probability"),
        "confidence": probability.get("confidence"),
        "reasons": probability.get("reasons", ()),
        "trade_plan_signal": trade_plan.get("signal"),
    }
