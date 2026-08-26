import pandas as pd

from dashboard.components.option_chain import _merge_authoritative_greeks


def _chain():
    return pd.DataFrame(
        [
            {
                "Strike": 24350,
                "CE_ID": 46999,
                "CE_LTP": 138.45,
                "CE_OI": 1878370,
                "CE_VOLUME": 11774425,
                "PE_ID": 47000,
                "PE_LTP": 89.95,
                "PE_OI": 1352520,
                "PE_VOLUME": 4984395,
            }
        ]
    )


def _greeks():
    return pd.DataFrame(
        [
            {
                "Strike": 24350,
                "CE_ID": 46999,
                "PE_ID": 47000,
                "CE_IV": 0.104749,
                "CE_DELTA": 0.514346,
                "CE_GAMMA": 0.001191,
                "CE_THETA": -4.2,
                "CE_VEGA": 12.3,
                "CE_RHO": 8.1,
                "PE_IV": 0.074321,
                "PE_DELTA": -0.481703,
                "PE_GAMMA": 0.001678,
                "PE_THETA": -3.8,
                "PE_VEGA": 11.7,
                "PE_RHO": -6.9,
            }
        ]
    )


def test_option_chain_ui_mapping_uses_same_contract_identity():
    merged = _merge_authoritative_greeks(_chain(), _greeks())

    assert merged.loc[0, "CE_IV"] == 0.104749
    assert merged.loc[0, "CE_DELTA"] == 0.514346
    assert merged.loc[0, "PE_IV"] == 0.074321
    assert merged.loc[0, "PE_DELTA"] == -0.481703


def test_option_chain_ui_mapping_does_not_fabricate_missing_greeks():
    greeks = _greeks().drop(columns=["PE_DELTA"])

    merged = _merge_authoritative_greeks(_chain(), greeks)

    assert "PE_DELTA" not in merged.columns
