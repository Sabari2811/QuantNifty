import pandas as pd

from analytics.oi.oi_flow_engine import OIFlowEngine


def _snapshots():
    previous = pd.DataFrame(
        [
            {"Strike": 24000, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000},
            {"Strike": 24100, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000},
            {"Strike": 24200, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000},
            {"Strike": 24300, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000},
        ]
    )
    current = previous.copy()

    # CE: +price/+OI, -price/+OI, -price/-OI, +price/-OI.
    current.loc[0, ["CE_LTP", "CE_OI"]] = [110, 1200]
    current.loc[1, ["CE_LTP", "CE_OI"]] = [90, 1200]
    current.loc[2, ["CE_LTP", "CE_OI"]] = [90, 800]
    current.loc[3, ["CE_LTP", "CE_OI"]] = [110, 800]

    # PE covers the same four cases in a different order.
    current.loc[0, ["PE_LTP", "PE_OI"]] = [90, 1200]
    current.loc[1, ["PE_LTP", "PE_OI"]] = [110, 800]
    current.loc[2, ["PE_LTP", "PE_OI"]] = [90, 800]
    current.loc[3, ["PE_LTP", "PE_OI"]] = [110, 1200]
    return current, previous


def test_all_price_oi_direction_combinations_are_classified():
    current, previous = _snapshots()
    result = OIFlowEngine().analyze(current, previous)
    table = result["table"]

    assert table["CE_FLOW"].tolist() == [
        "LONG_BUILDUP",
        "SHORT_BUILDUP",
        "LONG_UNWINDING",
        "SHORT_COVERING",
    ]
    assert table["PE_FLOW"].tolist() == [
        "SHORT_BUILDUP",
        "SHORT_COVERING",
        "LONG_UNWINDING",
        "LONG_BUILDUP",
    ]


def test_summary_counts_match_row_level_classification():
    current, previous = _snapshots()
    summary = OIFlowEngine().analyze(current, previous)["summary"]

    assert summary["status"] == "READY"
    assert summary["total_strikes"] == 4
    assert summary["call"] == {
        "long_buildup": 1,
        "short_buildup": 1,
        "long_unwinding": 1,
        "short_covering": 1,
        "no_change": 0,
        "unknown": 0,
    }
    assert summary["put"] == {
        "long_buildup": 1,
        "short_buildup": 1,
        "long_unwinding": 1,
        "short_covering": 1,
        "no_change": 0,
        "unknown": 0,
    }


def test_unmatched_current_strike_is_unknown_not_zero_baseline_flow():
    previous = pd.DataFrame([
        {"Strike": 24000, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000}
    ])
    current = pd.DataFrame([
        {"Strike": 24000, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 100, "PE_OI": 1000},
        {"Strike": 24100, "CE_LTP": 50, "CE_OI": 500, "PE_LTP": 150, "PE_OI": 1500},
    ])

    result = OIFlowEngine().analyze(current, previous)
    table = result["table"]
    summary = result["summary"]

    assert table.loc[1, "CE_FLOW"] == "UNKNOWN"
    assert table.loc[1, "PE_FLOW"] == "UNKNOWN"
    assert summary["call"]["unknown"] == 1
    assert summary["put"]["unknown"] == 1
    assert summary["call"]["long_unwinding"] == 0
    assert summary["put"]["long_buildup"] == 0
