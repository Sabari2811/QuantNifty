from __future__ import annotations

from types import SimpleNamespace

from engine.replay_engine import ReplayEngine


class FakeSimulationProvider:

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def current_snapshot(self):
        return self.snapshot


def build_snapshot():
    return SimpleNamespace(
        timestamp="21-Aug-2026 09:25:00",
        cycle_no=7,
        symbol="NIFTY",
        spot=24270.85,
        option_chain=SimpleNamespace(
            copy=lambda: "OPTION_CHAIN"
        ),
        greeks=SimpleNamespace(
            copy=lambda: "GREEKS"
        ),
        analytics={"test": 123},
        decision="DECISION",
        explanation="EXPLANATION",
    )


def test_replay_engine_preserves_authoritative_snapshot():

    snapshot = build_snapshot()

    provider = FakeSimulationProvider(snapshot)

    engine = ReplayEngine(provider)

    ctx = engine.run_cycle()

    assert ctx.snapshot is snapshot


def test_replay_engine_renders_snapshot_data_into_runtime_context():

    snapshot = build_snapshot()

    provider = FakeSimulationProvider(snapshot)

    engine = ReplayEngine(provider)

    ctx = engine.run_cycle()

    assert ctx.timestamp == snapshot.timestamp
    assert ctx.cycle_no == snapshot.cycle_no
    assert ctx.symbol == snapshot.symbol
    assert ctx.spot == snapshot.spot

    assert ctx.option_chain == "OPTION_CHAIN"
    assert ctx.greeks_df == "GREEKS"

    assert ctx.analytics is snapshot.analytics
    assert ctx.decision is snapshot.decision
    assert ctx.explanation is snapshot.explanation

    assert ctx.runtime_status == "REPLAY"