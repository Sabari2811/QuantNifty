import json
from types import SimpleNamespace

import pandas as pd

from recording.snapshot_recorder import SnapshotRecorder


def _ctx(intelligence):
    return SimpleNamespace(
        timestamp="26-Aug-2026 04:30:00",
        cycle_no=1,
        symbol="NIFTY",
        spot=25000.0,
        expiry="",
        runtime_status="IDLE",
        regime={},
        trade_status="",
        trade_block_reason="",
        data_provenance=None,
        analytics={},
        decision={},
        explanation={},
        intelligence=intelligence,
        option_chain=pd.DataFrame([{"Strike": 25000}]),
        greeks_df=pd.DataFrame([{"Strike": 25000}]),
    )


def test_recorder_skips_snapshot_without_intelligence(tmp_path):
    recorder = SnapshotRecorder(root=tmp_path)
    result = recorder.save(_ctx(None))

    assert result is False
    assert list(tmp_path.rglob("manifest.json")) == []


def test_recorder_skips_empty_intelligence(tmp_path):
    recorder = SnapshotRecorder(root=tmp_path)
    result = recorder.save(_ctx({}))

    assert result is False
    assert list(tmp_path.rglob("intelligence.json")) == []


def test_recorder_persists_populated_intelligence(tmp_path):
    intelligence = {"direction": "NEUTRAL", "conviction": 32.0}
    recorder = SnapshotRecorder(root=tmp_path)

    result = recorder.save(_ctx(intelligence))

    assert result is True
    files = list(tmp_path.rglob("intelligence.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload == intelligence
