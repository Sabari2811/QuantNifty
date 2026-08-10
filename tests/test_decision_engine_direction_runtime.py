from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.decision_engine import DecisionEngine

import pandas as pd


def canonical_greeks_df():
    return pd.DataFrame([
        {
            "Strike": 24200,
            "CE_ID": 1001,
            "CE_LTP": 165.0,
            "CE_BID": 164.5,
            "CE_ASK": 165.5,
            "CE_OI": 210000,
            "CE_VOLUME": 110000,
            "CE_IV": 14.8,
            "CE_DELTA": 0.48,
            "CE_GAMMA": 0.019,
            "CE_THETA": -13.2,
            "CE_VEGA": 8.7,
            "PE_ID": 1002,
            "PE_LTP": 120.0,
            "PE_BID": 119.5,
            "PE_ASK": 120.5,
            "PE_OI": 230000,
            "PE_VOLUME": 105000,
            "PE_IV": 14.4,
            "PE_DELTA": -0.44,
            "PE_GAMMA": 0.018,
            "PE_THETA": -12.8,
            "PE_VEGA": 8.5,
            "Expiry": "31-Jul-2026",
        },
        {
            "Strike": 24300,
            "CE_ID": 1003,
            "CE_LTP": 180.0,
            "CE_BID": 179.5,
            "CE_ASK": 180.5,
            "CE_OI": 250000,
            "CE_VOLUME": 120000,
            "CE_IV": 14.2,
            "CE_DELTA": 0.52,
            "CE_GAMMA": 0.018,
            "CE_THETA": -12.5,
            "CE_VEGA": 8.4,
            "PE_ID": 1004,
            "PE_LTP": 135.0,
            "PE_BID": 134.5,
            "PE_ASK": 135.5,
            "PE_OI": 220000,
            "PE_VOLUME": 100000,
            "PE_IV": 14.6,
            "PE_DELTA": -0.47,
            "PE_GAMMA": 0.019,
            "PE_THETA": -13.0,
            "PE_VEGA": 8.6,
            "Expiry": "31-Jul-2026",
        },
        {
            "Strike": 24400,
            "CE_ID": 1005,
            "CE_LTP": 142.0,
            "CE_BID": 141.5,
            "CE_ASK": 142.5,
            "CE_OI": 180000,
            "CE_VOLUME": 95000,
            "CE_IV": 13.9,
            "CE_DELTA": 0.46,
            "CE_GAMMA": 0.017,
            "CE_THETA": -11.8,
            "CE_VEGA": 8.1,
            "PE_ID": 1006,
            "PE_LTP": 150.0,
            "PE_BID": 149.5,
            "PE_ASK": 150.5,
            "PE_OI": 190000,
            "PE_VOLUME": 90000,
            "PE_IV": 14.9,
            "PE_DELTA": -0.51,
            "PE_GAMMA": 0.017,
            "PE_THETA": -13.4,
            "PE_VEGA": 8.8,
            "Expiry": "31-Jul-2026",
        },
    ])


def _snapshot(signal_name, institutional_score):
    analytics = {
        "dealer": {
            "dealer_gamma": "LONG",
            "market_mode": "TRENDING",
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
            "gamma_flip": 24300,
            "total_gex": 1250000,
            "expected_volatility": "NORMAL",
            "call_wall": 24400,
            "gamma_wall": 24300,
            "put_wall": 24100,
        },
        "dealer_flow": {
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
        },
        "liquidity": {
            "support": 24200,
            "resistance": 24500,
            "absorption": {
                "count": 2
            },
            "order_imbalance": {
                "buy_pressure": True,
                "sell_pressure": False,
            },
        },
        "market_structure": {
            "bias": "BULLISH",
            "structure": "TRENDING",
        },
        "pcr": {
            "oi_pcr": 1.20,
        },
        "expected_move": {
            "upper": 24600,
            "lower": 24000,
        },
        "iv_skew": {
            "market_sentiment": "BULLISH",
        },
        "iv_smile": {},
        "atr": {
            "volatility": "NORMAL",
            "atr": 155,
        },
        "prediction": {
            "prediction_score": 88,
        },
        "signal": {
            "signal": signal_name,
            "confidence": 80,
            "spot": 24310,
            "reasons": [],
        },
        "institutional_score": institutional_score,
    }

    # --------------------------------------------------------
    # Direction-aware PUT runtime fixture
    # --------------------------------------------------------
    #
    # Keep the production engines untouched.  For the BUY PUT
    # runtime regression, provide bearish evidence so the test
    # represents a coherent PUT setup rather than a bullish
    # market forced into a PUT signal.
    #
    if signal_name == "BUY PUT":
        analytics["dealer"]["dealer_gamma"] = "SHORT"
        analytics["dealer"]["total_gex"] = -1250000

        analytics["liquidity"]["order_imbalance"] = {
            "buy_pressure": False,
            "sell_pressure": True,
        }

        analytics["market_structure"]["bias"] = "BEARISH"
        analytics["pcr"]["oi_pcr"] = 0.80
        analytics["iv_skew"]["market_sentiment"] = "BEARISH"
    return MarketSnapshot().save(
        greeks_df=canonical_greeks_df(),
        spot=24310,
        analytics=analytics,
    )


def test_decision_engine_preserves_buy_call_direction():
    snapshot = _snapshot(
        "BUY CALL",
        {"score": 69},
    )

    decision = DecisionEngine().build(snapshot)

    assert decision.signal.name == "BUY CALL"


def test_decision_engine_preserves_buy_put_direction():
    snapshot = _snapshot(
        "BUY PUT",
        {"score": 69},
    )

    decision = DecisionEngine().build(snapshot)

    assert decision.signal.name == "BUY PUT"


def test_decision_engine_preserves_wait_direction():
    snapshot = _snapshot(
        "WAIT",
        {"score": 13},
    )

    decision = DecisionEngine().build(snapshot)

    assert decision.signal.name == "WAIT"
