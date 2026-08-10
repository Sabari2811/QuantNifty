from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.execution.execution_engine import ExecutionEngine
from decision.models import Decision

import pandas as pd


def canonical_greeks_df():
    return pd.DataFrame([
        {
            "Strike": 24200, "CE_ID": 1001, "CE_LTP": 165.0,
            "CE_BID": 164.5, "CE_ASK": 165.5, "CE_OI": 210000,
            "CE_VOLUME": 110000, "CE_IV": 14.8, "CE_DELTA": 0.48,
            "CE_GAMMA": 0.019, "CE_THETA": -13.2, "CE_VEGA": 8.7,
            "PE_ID": 1002, "PE_LTP": 120.0, "PE_BID": 119.5,
            "PE_ASK": 120.5, "PE_OI": 230000, "PE_VOLUME": 105000,
            "PE_IV": 14.4, "PE_DELTA": -0.44, "PE_GAMMA": 0.018,
            "PE_THETA": -12.8, "PE_VEGA": 8.5, "Expiry": "31-Jul-2026",
        },
        {
            "Strike": 24300, "CE_ID": 1003, "CE_LTP": 180.0,
            "CE_BID": 179.5, "CE_ASK": 180.5, "CE_OI": 250000,
            "CE_VOLUME": 120000, "CE_IV": 14.2, "CE_DELTA": 0.52,
            "CE_GAMMA": 0.018, "CE_THETA": -12.5, "CE_VEGA": 8.4,
            "PE_ID": 1004, "PE_LTP": 135.0, "PE_BID": 134.5,
            "PE_ASK": 135.5, "PE_OI": 220000, "PE_VOLUME": 100000,
            "PE_IV": 14.6, "PE_DELTA": -0.47, "PE_GAMMA": 0.019,
            "PE_THETA": -13.0, "PE_VEGA": 8.6, "Expiry": "31-Jul-2026",
        },
        {
            "Strike": 24400, "CE_ID": 1005, "CE_LTP": 142.0,
            "CE_BID": 141.5, "CE_ASK": 142.5, "CE_OI": 180000,
            "CE_VOLUME": 95000, "CE_IV": 13.9, "CE_DELTA": 0.46,
            "CE_GAMMA": 0.017, "CE_THETA": -11.8, "CE_VEGA": 8.1,
            "PE_ID": 1006, "PE_LTP": 150.0, "PE_BID": 149.5,
            "PE_ASK": 150.5, "PE_OI": 190000, "PE_VOLUME": 90000,
            "PE_IV": 14.9, "PE_DELTA": -0.51, "PE_GAMMA": 0.017,
            "PE_THETA": -13.4, "PE_VEGA": 8.8, "Expiry": "31-Jul-2026",
        },
    ])


def test_execution_plan_builds_from_canonical_option_schema():
    snapshot = MarketSnapshot().save(
        greeks_df=canonical_greeks_df(),
        spot=24310,
        analytics={
            "dealer": {
                "call_wall": 24400,
                "gamma_wall": 24300,
                "put_wall": 24100,
                "gamma_flip": 24200,
            }
        },
    )

    decision = Decision()
    decision.valid = True
    decision.signal.name = "BUY CALL"

    result = ExecutionEngine().prepare(decision, snapshot)

    assert result is not None
