import pandas as pd

from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.decision_engine import DecisionEngine
from decision.models import Decision
from decision.option_contract import OptionContract


def canonical_greeks_df():
    return pd.DataFrame([
        {
            "Strike": 24350, "CE_ID": 1001, "CE_LTP": 175.0, "CE_BID": 174.5,
            "CE_ASK": 175.5, "CE_OI": 210000, "CE_VOLUME": 110000, "CE_IV": 14.0,
            "CE_DELTA": 0.48, "CE_GAMMA": 0.018, "CE_THETA": -12.0, "CE_VEGA": 8.2,
            "PE_ID": 1002, "PE_LTP": 160.0, "PE_BID": 159.5, "PE_ASK": 160.5,
            "PE_OI": 205000, "PE_VOLUME": 105000, "PE_IV": 14.5, "PE_DELTA": -0.48,
            "PE_GAMMA": 0.018, "PE_THETA": -12.5, "PE_VEGA": 8.4, "Expiry": "31-Jul-2026",
        },
        {
            "Strike": 24400, "CE_ID": 1003, "CE_LTP": 182.45, "CE_BID": 182.0,
            "CE_ASK": 183.0, "CE_OI": 180000, "CE_VOLUME": 95000, "CE_IV": 13.9,
            "CE_DELTA": 0.46, "CE_GAMMA": 0.017, "CE_THETA": -11.8, "CE_VEGA": 8.1,
            "PE_ID": 1004, "PE_LTP": 150.0, "PE_BID": 149.5, "PE_ASK": 150.5,
            "PE_OI": 190000, "PE_VOLUME": 90000, "PE_IV": 14.9, "PE_DELTA": -0.51,
            "PE_GAMMA": 0.017, "PE_THETA": -13.4, "PE_VEGA": 8.8, "Expiry": "31-Jul-2026",
        },
    ])


def test_decision_engine_v2_uses_market_snapshot_contract():
    analytics = {
        "dealer": {
            "dealer_gamma": "LONG", "gamma_flip": 24200, "gamma_wall": 24300,
            "call_wall": 24400, "put_wall": 24100,
        },
        "prediction": {"prediction_score": 88},
        "institutional_score": {"institutional": {"score": 76, "max_score": 100}},
        "pcr": {"bias": "BULLISH"},
        "expected_move": {"expected_move": 185},
        "max_pain": {"max_pain": 24250},
        "atr": {"atr": 155},
    }

    snapshot = MarketSnapshot().save(
        greeks_df=canonical_greeks_df(),
        spot=24300,
        analytics=analytics,
    )

    decision = DecisionEngine().build(snapshot)

    assert isinstance(decision, Decision)
    assert decision.market.dealer == "LONG"
    assert "final" in decision.score
    assert decision.signal.name in {"BUY CALL", "BUY PUT", "WAIT"}

    if decision.trade.contract is not None:
        assert isinstance(decision.trade.contract, OptionContract)
        assert decision.trade.contract.option_type in {"CE", "PE"}
