import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from recording.snapshot_manifest import SnapshotManifest
from recording.snapshot_recorder import SnapshotRecorder
from simulation.replay_loader import ReplayLoader


def _provenance():
    return RuntimeDataProvenance(
        spot=AcquisitionProvenance(
            source="INDMoney index quote",
            acquired_at=datetime(2026, 8, 24, 4, 55, 12, 123456, tzinfo=timezone.utc),
            expected_count=1,
            received_count=1,
            missing_count=0,
            freshness_verified=True,
            freshness_seconds=1.25,
            reasons=("provider_timestamp",),
        ),
        option_chain=AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=datetime(2026, 8, 24, 4, 55, 13, 654321, tzinfo=timezone.utc),
            expected_count=22,
            received_count=20,
            missing_count=2,
            freshness_verified=False,
            freshness_seconds=None,
            reasons=("two_contracts_missing", "provider_timestamp_unavailable"),
        ),
        candles=AcquisitionProvenance(
            source="INDMoney historical candles:NIDX_40000001",
            acquired_at=datetime(2026, 8, 24, 4, 55, 14, 123456, tzinfo=timezone.utc),
            expected_count=225,
            received_count=225,
            missing_count=0,
            freshness_verified=False,
            freshness_seconds=None,
            reasons=("provider_candle_timestamp_not_used_for_freshness",),
        ),
    )


def _runtime_payload(provenance):
    return {
        "data_provenance": {
            name: {
                "source": item.source,
                "acquired_at": item.acquired_at.isoformat(),
                "expected_count": item.expected_count,
                "received_count": item.received_count,
                "missing_count": item.missing_count,
                "freshness_verified": item.freshness_verified,
                "freshness_seconds": item.freshness_seconds,
                "reasons": list(item.reasons),
            }
            for name, item in (("spot", provenance.spot), ("option_chain", provenance.option_chain), ("candles", provenance.candles))
            if item is not None
        }
    }


def _canonical_ctx(provenance):
    return SimpleNamespace(
        timestamp="24-Aug-2026 04:55:15",
        cycle_no=1,
        symbol="NIFTY",
        spot=24252.0,
        expiry="25-Aug-2026",
        runtime_status="IDLE",
        regime="TRENDING",
        trade_status="WAIT",
        trade_block_reason="",
        data_provenance=provenance,
        analytics={"gamma": 1.0},
        decision={"signal": {"name": "WAIT"}},
        explanation={"text": "range"},
        intelligence={"direction": "NEUTRAL", "conviction": 32.0},
        option_chain=pd.DataFrame([{"Strike": 24250}]),
        greeks_df=pd.DataFrame([{"Strike": 24250, "CE_IV": 0.2}]),
    )


def test_runtime_provenance_round_trips_without_semantic_loss(tmp_path):
    original = _provenance()
    encoded = _runtime_payload(original)

    path = tmp_path / "runtime.json"
    path.write_text(json.dumps(encoded), encoding="utf-8")

    restored = RuntimeDataProvenance.from_dict(
        json.loads(path.read_text(encoding="utf-8"))["data_provenance"]
    )

    assert restored == original


def test_snapshot_recorder_to_replay_loader_preserves_provenance(tmp_path):
    original = _provenance()
    recorder = SnapshotRecorder(root=tmp_path)
    assert recorder.save(_canonical_ctx(original)) is True
    folder = tmp_path / "24-Aug-2026" / "000001_04-55-15"

    snapshot = ReplayLoader().load(folder)

    assert snapshot.data_provenance == original
    assert snapshot.intelligence["direction"] == "NEUTRAL"
    assert snapshot.data_provenance.spot.freshness_verified is True
    assert snapshot.data_provenance.spot.freshness_seconds == 1.25
    assert snapshot.data_provenance.option_chain.received_count == 20
    assert snapshot.data_provenance.option_chain.missing_count == 2
    assert snapshot.data_provenance.candles.reasons == (
        "provider_candle_timestamp_not_used_for_freshness",
    )


def test_replay_loader_restores_canonical_provenance(tmp_path):
    original = _provenance()
    folder = tmp_path / "snapshot"
    folder.mkdir()
    SnapshotManifest().save(folder)

    runtime = {
        "timestamp": "24-Aug-2026 04:55:15",
        "cycle_no": 1,
        "symbol": "NIFTY",
        **_runtime_payload(original),
    }
    (folder / "runtime.json").write_text(json.dumps(runtime), encoding="utf-8")
    (folder / "intelligence.json").write_text(
        json.dumps({"direction": "NEUTRAL", "conviction": 32.0}),
        encoding="utf-8",
    )

    snapshot = ReplayLoader().load(folder)

    assert snapshot.data_provenance == original
    assert snapshot.intelligence["direction"] == "NEUTRAL"
    assert snapshot.data_provenance.spot.freshness_verified is True
    assert snapshot.data_provenance.spot.freshness_seconds == 1.25
    assert snapshot.data_provenance.option_chain.reasons == (
        "two_contracts_missing",
        "provider_timestamp_unavailable",
    )


def test_replay_loader_preserves_missing_provenance_as_empty_contract(tmp_path):
    folder = tmp_path / "legacy_snapshot"
    folder.mkdir()
    SnapshotManifest().save(folder)
    (folder / "runtime.json").write_text(
        json.dumps({"timestamp": "24-Aug-2026 04:55:15"}),
        encoding="utf-8",
    )
    (folder / "intelligence.json").write_text(
        json.dumps({"direction": "NEUTRAL", "conviction": 0.0}),
        encoding="utf-8",
    )

    snapshot = ReplayLoader().load(folder)

    assert snapshot.data_provenance == RuntimeDataProvenance()
    assert snapshot.data_provenance.complete is False
    assert snapshot.intelligence["direction"] == "NEUTRAL"
