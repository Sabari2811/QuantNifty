import pandas as pd

from dashboard.components.option_chain import _merge_authoritative_greeks


def test_option_chain_ui_projection_preserves_quote_and_greek_fields():
    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "CE_LTP": 120.5,
                "CE_BID": 120.0,
                "CE_ASK": 121.0,
                "CE_OI": 50000,
                "CE_VOLUME": 1200,
                "PE_ID": 222,
                "PE_LTP": 95.2,
                "PE_BID": 95.0,
                "PE_ASK": 95.5,
                "PE_OI": 47000,
                "PE_VOLUME": 900,
            }
        ]
    )
    greeks = option_chain.copy()
    greeks["CE_IV"] = 0.18
    greeks["CE_DELTA"] = 0.52
    greeks["CE_GAMMA"] = 0.001
    greeks["CE_THETA"] = -12.0
    greeks["CE_VEGA"] = 8.0
    greeks["CE_RHO"] = 4.0
    greeks["PE_IV"] = 0.21
    greeks["PE_DELTA"] = -0.48
    greeks["PE_GAMMA"] = 0.0011
    greeks["PE_THETA"] = -10.0
    greeks["PE_VEGA"] = 7.5
    greeks["PE_RHO"] = -3.5

    projected = _merge_authoritative_greeks(option_chain, greeks)
    row = projected.iloc[0]

    assert row["CE_BID"] == 120.0
    assert row["CE_ASK"] == 121.0
    assert row["CE_OI"] == 50000
    assert row["CE_VOLUME"] == 1200
    assert row["PE_BID"] == 95.0
    assert row["PE_ASK"] == 95.5
    assert row["PE_OI"] == 47000
    assert row["PE_VOLUME"] == 900
    assert row["CE_IV"] == 0.18
    assert row["PE_IV"] == 0.21


def test_option_chain_ui_projection_preserves_authoritative_analytics_fields():
    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "CE_LTP": 120.5,
                "CE_BID": 120.0,
                "CE_ASK": 121.0,
                "CE_OI": 50000,
                "CE_VOLUME": 1200,
                "PE_ID": 222,
                "PE_LTP": 95.2,
                "PE_BID": 95.0,
                "PE_ASK": 95.5,
                "PE_OI": 47000,
                "PE_VOLUME": 900,
            }
        ]
    )
    greeks = option_chain.copy()
    greeks["CE_IV"] = 0.18
    greeks["CE_DELTA"] = 0.52
    greeks["CE_GAMMA"] = 0.001
    greeks["CE_THETA"] = -12.0
    greeks["CE_VEGA"] = 8.0
    greeks["CE_RHO"] = 4.0
    greeks["PE_IV"] = 0.21
    greeks["PE_DELTA"] = -0.48
    greeks["PE_GAMMA"] = 0.0011
    greeks["PE_THETA"] = -10.0
    greeks["PE_VEGA"] = 7.5
    greeks["PE_RHO"] = -3.5
    greeks["NET_GEX"] = 123456.0
    greeks["NET_DEX"] = -98765.0
    greeks["NET_VANNA"] = 12.5
    greeks["NET_CHARM"] = -8.25
    greeks["CE_OI_CHANGE"] = 1500
    greeks["PE_OI_CHANGE"] = -900
    greeks["CE_FLOW"] = "LONG_BUILDUP"
    greeks["PE_FLOW"] = "SHORT_COVERING"
    greeks["_PREV_SNAPSHOT_MATCH"] = True

    projected = _merge_authoritative_greeks(option_chain, greeks)
    row = projected.iloc[0]

    assert row["NET_GEX"] == 123456.0
    assert row["NET_DEX"] == -98765.0
    assert row["NET_VANNA"] == 12.5
    assert row["NET_CHARM"] == -8.25
    assert row["CE_OI_CHANGE"] == 1500
    assert row["PE_OI_CHANGE"] == -900
    assert row["CE_FLOW"] == "LONG_BUILDUP"
    assert row["PE_FLOW"] == "SHORT_COVERING"
    assert row["_PREV_SNAPSHOT_MATCH"] is True


def test_option_chain_ui_projection_does_not_invent_missing_quote_fields():
    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "CE_LTP": 120.5,
                "CE_BID": None,
                "CE_ASK": None,
                "CE_OI": 50000,
                "CE_VOLUME": 1200,
                "PE_ID": 222,
                "PE_LTP": 95.2,
                "PE_BID": 95.0,
                "PE_ASK": 95.5,
                "PE_OI": 47000,
                "PE_VOLUME": 900,
            }
        ]
    )
    greeks = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "PE_ID": 222,
                "CE_IV": 0.18,
                "CE_DELTA": 0.52,
                "CE_GAMMA": 0.001,
                "CE_THETA": -12.0,
                "CE_VEGA": 8.0,
                "CE_RHO": 4.0,
                "PE_IV": 0.21,
                "PE_DELTA": -0.48,
                "PE_GAMMA": 0.0011,
                "PE_THETA": -10.0,
                "PE_VEGA": 7.5,
                "PE_RHO": -3.5,
            }
        ]
    )

    projected = _merge_authoritative_greeks(option_chain, greeks)
    row = projected.iloc[0]

    assert pd.isna(row["CE_BID"])
    assert pd.isna(row["CE_ASK"])
    assert row["PE_BID"] == 95.0
    assert row["PE_ASK"] == 95.5
