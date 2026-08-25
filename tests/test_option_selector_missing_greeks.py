import pandas as pd

from decision.constants import OptionType
from decision.execution.option_selector import OptionSelector


class Snapshot:
    def __init__(self, greeks_df):
        self.greeks_df = greeks_df


def _row(**overrides):
    row = {
        "Strike": 25000,
        "CE_LTP": 100.0,
        "CE_BID": 99.0,
        "CE_ASK": 101.0,
        "CE_VOLUME": 1000,
        "CE_OI": 5000,
        "CE_IV": 0.20,
        "CE_DELTA": 0.50,
        "CE_GAMMA": 0.001,
        "CE_THETA": -10.0,
        "CE_VEGA": 20.0,
        "PE_LTP": 100.0,
        "PE_BID": 99.0,
        "PE_ASK": 101.0,
        "PE_VOLUME": 1000,
        "PE_OI": 5000,
        "PE_IV": 0.20,
        "PE_DELTA": -0.50,
        "PE_GAMMA": 0.001,
        "PE_THETA": -10.0,
        "PE_VEGA": 20.0,
    }
    row.update(overrides)
    return row


def test_option_selector_rejects_none_greek_instead_of_converting_to_zero():
    selector = OptionSelector()
    snapshot = Snapshot(pd.DataFrame([_row(CE_IV=None)]))

    assert selector.select(snapshot, 25000, OptionType.CE.value) is None


def test_option_selector_accepts_complete_contract():
    selector = OptionSelector()
    snapshot = Snapshot(pd.DataFrame([_row()]))

    contract = selector.select(snapshot, 25000, OptionType.CE.value)

    assert contract is not None
    assert contract.iv == 0.20
    assert contract.delta == 0.50
    assert contract.gamma == 0.001
