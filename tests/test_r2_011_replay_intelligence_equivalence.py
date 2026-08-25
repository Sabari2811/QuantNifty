import json

from recording.snapshot_manifest import SnapshotManifest
from simulation.replay_equivalence import compare_replay_outputs
from simulation.replay_loader import ReplayLoader


def test_replay_equivalence_accepts_dataclass_like_numeric_differences():
    expected_decision = {
        "signal": {"name": "WAIT", "confidence": 32},
        "score": {"final": 32.0},
    }
    actual_decision = {
        "signal": {"name": "WAIT", "confidence": 32},
        "score": {"final": 32.0000000001},
    }
    expected_intelligence = {
        "direction": "NEUTRAL",
        "conviction": 32.0,
        "opportunity_quality": 41.5,
    }
    actual_intelligence = {
        "direction": "NEUTRAL",
        "conviction": 32.0000000001,
        "opportunity_quality": 41.5000000001,
    }

    result = compare_replay_outputs(
        expected_decision,
        actual_decision,
        expected_intelligence,
        actual_intelligence,
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
        manifest.intelligence: {
            "direction": "NEUTRAL",
            "conviction": 32.0,
            "opportunity_quality": 41.5,
        },
    }.items():
        (tmp_path / filename).write_text(json.dumps(payload), encoding="utf-8")

    snapshot = ReplayLoader().load(tmp_path)

    assert snapshot.intelligence["direction"] == "NEUTRAL"
    assert snapshot.intelligence["conviction"] == 32.0
