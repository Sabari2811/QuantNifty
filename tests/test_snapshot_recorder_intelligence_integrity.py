from types import SimpleNamespace

import pytest

from recording.snapshot_recorder import SnapshotRecorder


class _Index:
    def append(self, ctx, folder):
        return None


def _ctx(intelligence):
    return SimpleNamespace(
        timestamp="26-Aug-2026 04:20:00",
        cycle_no=1,
        symbol="NIFTY",
        spot=25000.0,
        expiry="",
        runtime_status="IDLE",
        regime=None,
        trade_status="",
        trade_block_reason="",
        data_provenance=None,
        analytics={"ok": True},
        decision={"signal": "WAIT"},
        explanation={"text": "test"},
        intelligence=intelligence,
        option_chain=None,
        greeks_df=None,
    )


def test_canonical_recorder_rejects_missing_intelligence(tmp_path):
    recorder = SnapshotRecorder(root=tmp_path)
    recorder.index = _Index()

    with pytest.raises(ValueError, match="populated intelligence artifact"):
        recorder.save(_ctx(None), tmp_path / "missing")


def test_canonical_recorder_rejects_empty_intelligence_dict(tmp_path):
    recorder = SnapshotRecorder(root=tmp_path)
    recorder.index = _Index()

    with pytest.raises(ValueError, match="populated intelligence artifact"):
        recorder.save(_ctx({}), tmp_path / "empty")


def test_canonical_recorder_persists_populated_intelligence(tmp_path):
    recorder = SnapshotRecorder(root=tmp_path)
    recorder.index = _Index()

    folder = tmp_path / "valid"
    recorder.save(_ctx({"direction": "NEUTRAL", "conviction": 42}), folder)

    assert (folder / "intelligence.json").exists()
    assert '"conviction": 42' in (folder / "intelligence.json").read_text(encoding="utf-8")
