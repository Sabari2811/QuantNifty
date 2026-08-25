import json
from types import SimpleNamespace

import pandas as pd

from core.data_provenance import RuntimeDataProvenance
from engine.market_data_pipeline import MarketDataPipeline
from recording.snapshot_manifest import SnapshotManifest
from simulation.replay_equivalence import compare_replay_outputs
from simulation.replay_loader import ReplayLoader
from simulation.replay_snapshot import ReplaySnapshot


def test_replay_equivalence_accepts_dataclass_like_numeric_differences():
    result = compare_replay_outputs(
        {"signal": {"name": "WAIT", "confidence": 32}, "score": {"final": 32.0}},
        {"signal": {"name": "WAIT", "confidence": 32}, "score": {"final": 32.0000000001}},
        {"direction": "NEUTRAL", "conviction": 32.0, "opportunity_quality": 41.5},
        {"direction": "NEUTRAL", "conviction": 32.0000000001, "opportunity_quality": 41.5000000001},
    )

    assert result.equivalent is True
    assert result.mismatches == ()


def test_replay_equivalence_reports_exact_field_paths_for_drift():
    result = compare_replay_outputs(
        {"signal": {"name": "BUY CALL"}},
        {"signal": {"name": "WAIT"}},
        {"direction": "BULLISH"},
        {"direction": "BEARISH"},
    )

    assert result.equivalent is False
    assert "decision.signal.name" in result.mismatches
    assert "intelligence.direction" in result.mismatches


def test_replay_loader_reads_canonical_intelligence_artifact(tmp_path):
    manifest = SnapshotManifest()
    manifest.save(tmp_path)

    for filename, payload in {
        manifest.runtime: {"data_provenance": {}},
        manifest.analytics: {"gamma": 1},
        manifest.decision: {"signal": {"name": "WAIT"}},
        manifest.explanation: {"text": "range"},
        manifest.intelligence: {"direction": "NEUTRAL", "conviction": 32.0},
    }.items():
        (tmp_path / filename).write_text(json.dumps(payload), encoding="utf-8")

    snapshot = ReplayLoader().load(tmp_path)

    assert snapshot.intelligence["direction"] == "NEUTRAL"
    assert snapshot.intelligence["conviction"] == 32.0


class _Provider:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def current_snapshot(self):
        return self.snapshot


def test_replay_pipeline_carries_recorded_intelligence_and_equivalence_expectations():
    snapshot = ReplaySnapshot(
        runtime={
            "timestamp": "24-Aug-2026 10:00:00",
            "cycle_no": 7,
            "symbol": "NIFTY",
            "spot": 25050.0,
        },
        analytics={"gamma": 1.0},
        decision={"signal": {"name": "WAIT"}},
        explanation={"text": "range"},
        intelligence={"direction": "NEUTRAL", "conviction": 32.0},
        data_provenance=RuntimeDataProvenance(),
        option_chain=pd.DataFrame([{"Strike": 25000}]),
        greeks=pd.DataFrame([{"Strike": 25000, "CE_IV": 0.2}]),
    )

    pipeline = MarketDataPipeline(
        provider=_Provider(snapshot),
        instrument=None,
        market=None,
        chain_manager=None,
        candle_manager=None,
    )
    ctx = SimpleNamespace()

    pipeline._run_replay(ctx)

    assert ctx.intelligence == snapshot.intelligence
    assert ctx.replay_expected_decision == snapshot.decision
    assert ctx.replay_expected_intelligence == snapshot.intelligence
    assert ctx.data_provenance == snapshot.data_provenance


def test_replay_equivalence_accepts_matching_canonical_outputs():
    result = compare_replay_outputs(
        {"signal": {"name": "WAIT", "confidence": 32}},
        {"signal": {"name": "WAIT", "confidence": 32}},
        {"direction": "NEUTRAL", "conviction": 32.0},
        {"direction": "NEUTRAL", "conviction": 32.0},
    )

    assert result.equivalent is True
    assert result.mismatches == ()
