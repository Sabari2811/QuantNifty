from analytics.signal.signal_engine import SignalEngine


def test_nifty_signal_requires_directional_confluence_for_call():
    result = SignalEngine().generate(
        {"dealer_gamma": "LONG"},
        {"bullish_probability": 75, "bearish_probability": 45, "confidence": 30, "bullish_confirmations": 2, "bearish_confirmations": 0},
        24500,
        market_structure={"bias": "BULLISH"},
        pcr={"sentiment": "NEUTRAL"},
        technical={},
    )
    assert result["signal"] == "BUY CALL"
    assert result["underlying"] == "NIFTY"


def test_nifty_signal_waits_when_probability_is_not_confirmed():
    result = SignalEngine().generate(
        {"dealer_gamma": "LONG"},
        {"bullish_probability": 72, "bearish_probability": 48, "confidence": 24, "bullish_confirmations": 1, "bearish_confirmations": 0},
        24500,
        market_structure={"bias": "NEUTRAL"},
        pcr={"sentiment": "NEUTRAL"},
        technical={},
    )
    assert result["signal"] == "WAIT"


def test_nifty_signal_requires_bearish_confluence_for_put():
    result = SignalEngine().generate(
        {"dealer_gamma": "SHORT"},
        {"bullish_probability": 35, "bearish_probability": 80, "confidence": 45, "bullish_confirmations": 0, "bearish_confirmations": 2},
        24500,
        market_structure={"bias": "BEARISH"},
        pcr={"sentiment": "BEARISH"},
        technical={},
    )
    assert result["signal"] == "BUY PUT"
