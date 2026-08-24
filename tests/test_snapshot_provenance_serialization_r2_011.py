import json
from types import SimpleNamespace
from datetime import datetime, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from recording.snapshot_recorder import SnapshotRecorder


def test_snapshot_runtime_persists_complete_data_provenance(tmp_path):
    provenance = RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=datetime(2026, 8, 24, 9, 15, tzinfo=timezone.utc),
            expected_count=22,
            received_count=22,
            missing_count=0,
            freshness_verified=True,
            freshness_seconds=1.25,
            reasons=("batch_complete",),
        ),
        candles=AcquisitionProvenance(
            source="INDMoney historical candles",
            acquired_at=datetime(2026, 8, 24, 9, 15, tzinfo=timezone.utc),
            expected_count=225,
            received_count=224,
            missing_count=1,
            freshness_verified=False,
            freshness_seconds=None,
            reasons=("freshness_unverified", "one_candle_missing"),
        ),
        spot=AcquisitionProvenance(
            source="INDMoney index quote",
            acquired_at=datetime(2026, 8, 24, 9, 15, tzinfo=timezone.utc),
            expected_count=1,
            received_count=1,
            missing_count=0,
            freshness_verified=True,
            freshness_seconds=0.4,
            reasons=(),
        ),
    )

    ctx = SimpleNamespace(
        timestamp="24-Aug-2026 09:15:00",
        cycle_no=1,
        symbol="NIFTY",
        spot=24252.0,
        expiry="25-Aug-2026",
        runtime_status="READY",
        regime="TRENDING",
        trade_status="WAIT",
        trade_block_reason="",
        data_provenance=provenance,
    )

    recorder = SnapshotRecorder(root=tmp_path)
    recorder._save_runtime(tmp_path, ctx)

    runtime = json.loads((tmp_path / "runtime.json").read_text(encoding="utf-8"))
    saved = runtime["data_provenance"]

    assert saved["option_chain"]["source"] == "INDMoney option quotes"
    assert saved["option_chain"]["acquired_at"] == "2026-08-24T09:15:00+00:00"
    assert saved["option_chain"]["expected_count"] == 22
    assert saved["option_chain"]["received_count"] == 22
    assert saved["option_chain"]["missing_count"] == 0
    assert saved["option_chain"]["freshness_verified"] is True
    assert saved["option_chain"]["freshness_seconds"] == 1.25
    assert saved["option_chain"]["reasons"] == ["batch_complete"]

    assert saved["candles"]["freshness_verified"] is False
    assert saved["candles"]["missing_count"] == 1
    assert saved["candles"]["reasons"] == ["freshness_unverified", "one_candle_missing"]

    assert saved["spot"]["received_count"] == 1
