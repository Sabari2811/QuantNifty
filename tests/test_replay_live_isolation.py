from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from engine.replay_engine import ReplayEngine
from simulation.replay_snapshot import ReplaySnapshot


class FakeReplayProvider:
    def __init__(self, snapshot):
        self._snapshot = snapshot

    def current_snapshot(self):
        return self._snapshot


def test_replay_restores_recorded_decision_without_creating_live_execution_state():
    recorded_decision = {"signal": "BUY CALL", "trade": {"symbol": "NIFTY"}}
    snapshot = ReplaySnapshot(
        runtime={
            "timestamp": "2026-09-07T09:15:00+05:30",
            "cycle_no": 7,
            "symbol": "NIFTY",
            "spot": 25000,
            "trade_status": "EXECUTED",
        },
        analytics={"expected_move": {"atm_strike": 25000}},
        decision=recorded_decision,
        option_chain=pd.DataFrame(),
        greeks=pd.DataFrame(),
    )

    ctx = ReplayEngine(FakeReplayProvider(snapshot)).run_cycle()

    assert ctx.runtime_status == "REPLAY"
    assert ctx.decision is recorded_decision
    assert ctx.trade_status == ""
    assert ctx.execution_intent is None
    assert ctx.execution_result is None
    assert ctx.execution_lifecycle == ""
    assert ctx.position_reconciliation is None
    assert ctx.position_recovery is None


def test_replay_does_not_import_live_decision_or_execution_attributes_from_snapshot():
    snapshot = ReplaySnapshot(
        runtime={
            "timestamp": "2026-09-07T09:16:00+05:30",
            "cycle_no": 8,
            "symbol": "NIFTY",
            "spot": 25010,
            "trade_status": "BLOCKED",
        },
        decision={"signal": "WAIT"},
    )
    snapshot.runtime["execution_result"] = SimpleNamespace(status="EXECUTED")
    snapshot.runtime["execution_intent"] = SimpleNamespace(client_order_id="live-should-not-leak")

    ctx = ReplayEngine(FakeReplayProvider(snapshot)).run_cycle()

    assert ctx.execution_result is None
    assert ctx.execution_intent is None
    assert ctx.trade_status == ""
