from analytics.scoring.score_engine import ScoreEngine


def _inputs():
    return {
        "dealer": {
            "dealer_gamma": "LONG",
            "market_mode": "TRENDING",
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
            "gamma_flip": 24300,
            "total_gex": 1250000,
            "expected_volatility": "NORMAL",
        },
        "dealer_flow": {
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
        },
        "liquidity": {
            "support": 24200,
            "resistance": 24500,
            "absorption": {"count": 2},
            "order_imbalance": {
                "buy_pressure": True,
                "sell_pressure": False,
            },
        },
        "market_structure": {
            "bias": "BULLISH",
            "structure": "TRENDING",
        },
        "pcr": {"oi_pcr": 1.20},
        "expected_move": {"upper": 24600, "lower": 24000},
        "iv_skew": {"market_sentiment": "BULLISH"},
        "iv_smile": {},
        "atr": {"volatility": "NORMAL"},
        "spot": 24350,
    }


def test_score_engine_buy_call_rewards_bullish_evidence():
    result = ScoreEngine().calculate(
        **_inputs(),
        signal={"signal": "BUY CALL"},
    )

    assert result["institutional"]["score"] == 69
    assert result["institutional"]["max_score"] == 100
    assert result["dealer_score"]["score"] == 20
    assert result["liquidity_score"]["score"] == 15
    assert result["gamma_score"]["score"] == 15
    assert result["structure_score"]["score"] == 10
    assert result["volatility_score"]["score"] == 9


def test_score_engine_buy_put_uses_direction_aware_conditions():
    data = _inputs()
    data["dealer"]["dealer_gamma"] = "SHORT"
    data["dealer"]["total_gex"] = -1250000
    data["liquidity"]["order_imbalance"] = {
        "buy_pressure": False,
        "sell_pressure": True,
    }
    data["market_structure"]["bias"] = "BEARISH"
    data["pcr"]["oi_pcr"] = 0.80
    data["iv_skew"]["market_sentiment"] = "BEARISH"

    result = ScoreEngine().calculate(
        **data,
        signal={"signal": "BUY PUT"},
    )

    assert result["institutional"]["score"] == 69
    assert result["dealer_score"]["score"] == 20
    assert result["liquidity_score"]["score"] == 15
    assert result["gamma_score"]["score"] == 15
    assert result["structure_score"]["score"] == 10
    assert result["volatility_score"]["score"] == 9


def test_score_engine_no_trade_does_not_create_directional_signal():
    result = ScoreEngine().calculate(
        **_inputs(),
        signal={"signal": "WAIT"},
    )

    assert result["institutional"]["score"] == 13
    assert result["institutional"]["signal"] == "NO TRADE"
    assert result["institutional"]["confidence"] == 13
    assert result["dealer_score"]["score"] == 5
    assert result["liquidity_score"]["score"] == 3
    assert result["gamma_score"]["score"] == 3
    assert result["structure_score"]["score"] == 0
    assert result["volatility_score"]["score"] == 2

