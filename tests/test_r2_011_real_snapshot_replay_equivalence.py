"""Real recorded-snapshot replay equivalence gate.

Set QUANTNIFTY_REPLAY_SNAPSHOT to a recorded snapshot directory, for example:
    data/snapshots/24-Aug-2026/000070_17-35-39

The test intentionally skips when no snapshot is supplied so the normal unit
suite remains independent of local runtime artifacts. When supplied, it runs
through the real ReplayLoader -> SimulationProvider -> MarketDataPipeline ->
LiveEngine(REPLAY_RECOMPUTE) path and requires zero decision/intelligence drift.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from engine.live_engine import LiveEngine
from simulation.replay_loader import ReplayLoader
from simulation.replay_source import ReplaySource
from providers.simulation_provider import SimulationProvider
from runtime.runtime_mode import RuntimeMode


class _SingleSnapshotSource(ReplaySource):
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def current(self):
        return self._snapshot

    def next(self):
        return self._snapshot

    def previous(self):
        return self._snapshot

    def seek(self, index: int):
        if index != 0:
            raise IndexError(index)
        return self._snapshot

    def has_next(self):
        return False

    def has_previous(self):
        return False

    def reset(self):
        return self._snapshot


def _snapshot_path() -> Path | None:
    value = os.environ.get("QUANTNIFTY_REPLAY_SNAPSHOT")
    if not value:
        return None
    path = Path(value)
    if not path.exists():
        pytest.fail(f"QUANTNIFTY_REPLAY_SNAPSHOT does not exist: {path}")
    return path


def test_real_recorded_snapshot_replays_to_identical_decision_and_intelligence():
    folder = _snapshot_path()
    if folder is None:
        pytest.skip("Set QUANTNIFTY_REPLAY_SNAPSHOT to run the real snapshot gate")

    snapshot = ReplayLoader().load(folder)
    assert snapshot.decision, "Recorded snapshot has no decision artifact"
    assert snapshot.intelligence, "Recorded snapshot has no intelligence artifact"

    provider = SimulationProvider(
        _SingleSnapshotSource(snapshot),
        runtime_mode=RuntimeMode.REPLAY_RECOMPUTE,
    )

    engine = LiveEngine(provider=provider)
    ctx = engine.build_context()

    equivalence = getattr(ctx, "replay_equivalence", None)
    assert equivalence is not None, "Replay equivalence was not evaluated"
    assert equivalence.equivalent, (
        "Canonical replay drift detected: "
        + ", ".join(equivalence.mismatches)
    )
    assert equivalence.mismatches == ()
