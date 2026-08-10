import pandas as pd

from analytics.oi.oi_flow_engine import OIFlowEngine


def test_oi_flow_engine_analyzes_option_flow():
    greeks = pd.DataFrame(
        [
            {
                "STRIKE": 24300,
                "CE_LTP": 100,
                "CE_OI": 1000,
                "PE_LTP": 80,
                "PE_OI": 500,
            },
            {
                "STRIKE": 24400,
                "CE_LTP": 120,
                "CE_OI": 1500,
                "PE_LTP": 90,
                "PE_OI": 800,
            },
            {
                "STRIKE": 24500,
                "CE_LTP": 0,
                "CE_OI": 0,
                "PE_LTP": 110,
                "PE_OI": 1200,
            },
        ]
    )

    result = OIFlowEngine().analyze(greeks)

    assert "summary" in result
    assert "table" in result

    assert len(result["table"]) == 3

    assert "CE_FLOW" in result["table"].columns
    assert "PE_FLOW" in result["table"].columns

    assert result["summary"]["total_strikes"] == 3

    assert "call" in result["summary"]
    assert "put" in result["summary"]

    assert "market_bias" in result["summary"]
    assert result["summary"]["market_bias"] in {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    }

    assert "trend" in result["summary"]
    assert result["summary"]["trend"] in {
        "TRENDING",
        "REVERSAL",
        "SIDEWAYS",
    }


def test_oi_flow_engine_classifies_flow_types():
    greeks = pd.DataFrame(
        [
            {
                "STRIKE": 24300,
                "CE_LTP": 100,
                "CE_OI": 1000,
                "PE_LTP": -100,
                "PE_OI": 1000,
            },
            {
                "STRIKE": 24400,
                "CE_LTP": -100,
                "CE_OI": 1000,
                "PE_LTP": 100,
                "PE_OI": 0,
            },
        ]
    )

    result = OIFlowEngine().analyze(greeks)

    table = result["table"]

    assert table.loc[0, "CE_FLOW"] == "LONG_BUILDUP"
    assert table.loc[0, "PE_FLOW"] == "SHORT_BUILDUP"

    assert table.loc[1, "CE_FLOW"] == "SHORT_BUILDUP"
    assert table.loc[1, "PE_FLOW"] == "SHORT_COVERING"


def test_oi_flow_engine_handles_empty_input():
    result = OIFlowEngine().analyze(pd.DataFrame())

    assert result["summary"] == {}
    assert result["table"].empty
