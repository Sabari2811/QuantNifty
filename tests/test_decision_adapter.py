from types import SimpleNamespace

from dashboard.decision_adapter import adapt_decision


def _dashboard():
    return SimpleNamespace(
        signal={"signal": "BUY PUT"},
        probability={
            "bullish_probability": 31,
            "bearish_probability": 72,
            "confidence": 68,
            "reasons": ("canonical reason",),
        },
        trade_plan={"signal": "BUY PUT"},
    )


def test_decision_adapter_uses_canonical_decision_fields():
    assert adapt_decision(_dashboard()) == {
        "signal": "BUY PUT",
        "bullish_probability": 31,
        "bearish_probability": 72,
        "confidence": 68,
        "reasons": ("canonical reason",),
        "trade_plan_signal": "BUY PUT",
    }


def test_decision_adapter_does_not_recompute_signal():
    dashboard = _dashboard()
    dashboard.signal = {"signal": "WAIT"}
    dashboard.probability["bullish_probability"] = 100
    dashboard.probability["bearish_probability"] = 0

    assert adapt_decision(dashboard)["signal"] == "WAIT"
