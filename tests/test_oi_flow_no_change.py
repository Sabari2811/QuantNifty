import pandas as pd

from analytics.oi.oi_flow_engine import OIFlowEngine


def test_zero_price_and_oi_delta_is_no_change():
    engine = OIFlowEngine()
    assert engine._classify(0.0, 0.0) == "NO_CHANGE"


def test_consecutive_identical_snapshots_report_no_change_not_unknown():
    previous = pd.DataFrame([
        {"Strike": 24300, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 80, "PE_OI": 1200},
        {"Strike": 24400, "CE_LTP": 90, "CE_OI": 1500, "PE_LTP": 100, "PE_OI": 900},
    ])
    result = OIFlowEngine().analyze(previous.copy(), previous)
    table = result["table"]
    summary = result["summary"]

    assert result["summary"]["status"] == "READY"
    assert table["CE_FLOW"].tolist() == ["NO_CHANGE", "NO_CHANGE"]
    assert table["PE_FLOW"].tolist() == ["NO_CHANGE", "NO_CHANGE"]
    assert summary["call"]["no_change"] == 2
    assert summary["put"]["no_change"] == 2
    assert summary["call"]["unknown"] == 0
    assert summary["put"]["unknown"] == 0


def test_first_snapshot_remains_unknown():
    current = pd.DataFrame([
        {"Strike": 24300, "CE_LTP": 100, "CE_OI": 1000, "PE_LTP": 80, "PE_OI": 1200}
    ])
    result = OIFlowEngine().analyze(current)
    assert result["summary"]["status"] == "AWAITING_PREVIOUS_SNAPSHOT"
    assert result["table"].loc[0, "CE_FLOW"] == "UNKNOWN"
    assert result["table"].loc[0, "PE_FLOW"] == "UNKNOWN"
    assert result["summary"]["call"]["unknown"] == 1
    assert result["summary"]["put"]["unknown"] == 1
    assert result["summary"]["call"]["no_change"] == 0
    assert result["summary"]["put"]["no_change"] == 0
