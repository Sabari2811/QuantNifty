from types import SimpleNamespace

import pandas as pd

from dashboard.components.live_trade_monitor import _option_row, _trade_values


def test_trade_values_map_execution_and_risk_fields():
    intent = SimpleNamespace(option_type="CE", strike=25000, quantity=75, limit_price=120.5)
    result = SimpleNamespace(filled_quantity=75, average_fill_price=121.0)
    trade = SimpleNamespace(option_type="CE", strike=25000, entry=121.0, stop_loss=101.0, target1=151.0, target2=171.0, quantity=75)
    dashboard = SimpleNamespace(
        trade_plan={
            "signal": "BUY_CALL",
            "option_type": "CE",
            "recommended_strike": 25000,
            "entry": 121.0,
            "stop_loss": 101.0,
            "target1": 151.0,
            "target2": 171.0,
        },
        execution_intent=intent,
        execution_result=result,
        position=SimpleNamespace(quantity=75, status="OPEN"),
        last_trade=None,
        option_chain=pd.DataFrame(),
    )
    values = _trade_values(dashboard)
    assert values["option_type"] == "CE"
    assert values["strike"] == 25000
    assert values["entry"] == 121.0
    assert values["stop_loss"] == 101.0
    assert values["target1"] == 151.0
    assert values["target2"] == 171.0
    assert values["quantity"] == 75
    assert values["open"] is True


def test_option_row_resolves_exact_nifty_contract():
    chain = pd.DataFrame([
        {"Strike": 25000, "CE_ID": 111, "CE_LTP": 121.5, "CE_BID": 121.0, "CE_ASK": 122.0,
         "PE_ID": 222, "PE_LTP": 98.5, "PE_BID": 98.0, "PE_ASK": 99.0},
    ])
    ce = _option_row(chain, 25000, "CE")
    pe = _option_row(chain, 25000, "PE")
    assert ce == {"security_id": 111, "ltp": 121.5, "bid": 121.0, "ask": 122.0}
    assert pe == {"security_id": 222, "ltp": 98.5, "bid": 98.0, "ask": 99.0}
