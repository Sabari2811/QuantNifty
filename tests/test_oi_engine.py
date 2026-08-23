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
    previous = pd.DataFrame(
        [
            {
                "Strike": 24300,
                "CE_ID": 1,
                "PE_ID": 2,
                "CE_LTP": 100,
                "CE_OI": 1000,
                "PE_LTP": 100,
                "PE_OI": 1000,
            },
            {
                "Strike": 24400,
                "CE_ID": 3,
                "PE_ID": 4,
                "CE_LTP": 100,
                "CE_OI": 1000,
                "PE_LTP": 100,
                "PE_OI": 1000,
            },
        ]
    )

    current = previous.copy()

    # ----------------------------------------------------------
    # Strike 24300
    #
    # CE: price ↑ + OI ↑ = LONG_BUILDUP
    # PE: price ↓ + OI ↑ = SHORT_BUILDUP
    # ----------------------------------------------------------

    current.loc[0, "CE_LTP"] = 110
    current.loc[0, "CE_OI"] = 1200

    current.loc[0, "PE_LTP"] = 90
    current.loc[0, "PE_OI"] = 1200

    # ----------------------------------------------------------
    # Strike 24400
    #
    # CE: price ↓ + OI ↑ = SHORT_BUILDUP
    # PE: price ↑ + OI ↓ = SHORT_COVERING
    # ----------------------------------------------------------

    current.loc[1, "CE_LTP"] = 90
    current.loc[1, "CE_OI"] = 1200

    current.loc[1, "PE_LTP"] = 110
    current.loc[1, "PE_OI"] = 800

    result = OIFlowEngine().analyze(
        current,
        previous,
    )

    table = result["table"]
    summary = result["summary"]

    # ----------------------------------------------------------
    # Row-level classification
    # ----------------------------------------------------------

    assert table.loc[0, "CE_FLOW"] == "LONG_BUILDUP"
    assert table.loc[0, "PE_FLOW"] == "SHORT_BUILDUP"

    assert table.loc[1, "CE_FLOW"] == "SHORT_BUILDUP"
    assert table.loc[1, "PE_FLOW"] == "SHORT_COVERING"

    # ----------------------------------------------------------
    # Summary aggregation
    #
    # These are the values consumed by the dashboard/UI.
    # ----------------------------------------------------------

    assert summary["total_strikes"] == 2

    assert summary["call"]["long_buildup"] == 1
    assert summary["call"]["short_buildup"] == 1
    assert summary["call"]["long_unwinding"] == 0
    assert summary["call"]["short_covering"] == 0

    assert summary["put"]["long_buildup"] == 0
    assert summary["put"]["short_buildup"] == 1
    assert summary["put"]["long_unwinding"] == 0
    assert summary["put"]["short_covering"] == 1


def test_oi_flow_engine_classifies_long_unwinding():
    previous = pd.DataFrame(
        [
            {
                "Strike": 24500,
                "CE_LTP": 100,
                "CE_OI": 1000,
                "PE_LTP": 100,
                "PE_OI": 1000,
            }
        ]
    )

    current = previous.copy()

    # Price ↓ + OI ↓ = LONG_UNWINDING
    current.loc[0, "CE_LTP"] = 90
    current.loc[0, "CE_OI"] = 800

    result = OIFlowEngine().analyze(
        current,
        previous,
    )

    table = result["table"]
    summary = result["summary"]

    assert (
        table.loc[0, "CE_FLOW"]
        == "LONG_UNWINDING"
    )

    assert summary["call"]["long_unwinding"] == 1
    assert summary["call"]["long_buildup"] == 0
    assert summary["call"]["short_buildup"] == 0
    assert summary["call"]["short_covering"] == 0


def test_oi_flow_engine_handles_empty_input():
    result = OIFlowEngine().analyze(
        pd.DataFrame()
    )

    assert result["summary"] == {}
    assert result["table"].empty