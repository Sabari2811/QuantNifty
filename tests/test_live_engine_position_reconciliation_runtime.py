from datetime import datetime

from engine.live_engine import LiveEngine
from execution.position_reconciliation_runtime import PositionReconciliationRuntimeDecision
from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionState, PositionStatus
from execution.reconciliation import ReconciliationReport, ReconciliationStatus


class FakeStore:
    def __init__(self, positions=()):
        self.positions = tuple(positions)

    def open_positions(self):
        return self.positions


def _open_position():
    return PositionState(
        client_order_id="client-1",
        broker_order_id="broker-1",
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        quantity=50,
        entry_price=100.0,
        current_price=110.0,
        stop_loss=90.0,
        target=120.0,
        opened_at=datetime(2026, 9, 5, 9, 15),
        status=PositionStatus.OPEN,
    )


def _engine_with_persisted_position():
    engine = object.__new__(LiveEngine)
    engine.ctx = type("Context", (), {})()
    engine.position_runtime_service = PositionRuntimeService(FakeStore((_open_position(),)))
    return engine


def test_live_engine_recovery_requires_explicit_reconciliation_before_continuation():
    engine = _engine_with_persisted_position()

    recovery = engine._recover_position_runtime_state()
    decision = engine._evaluate_position_reconciliation(recovery, None)

    assert isinstance(decision, PositionReconciliationRuntimeDecision)
    assert decision.safe_to_continue is False
    assert decision.requires_manual_resolution is False
    assert "reconciliation" in decision.reason.lower()
    assert engine.ctx.position_reconciliation == decision


def test_live_engine_recovery_allows_continuation_only_after_match():
    engine = _engine_with_persisted_position()

    recovery = engine._recover_position_runtime_state()
    report = ReconciliationReport(
        status=ReconciliationStatus.MATCH,
        local_count=1,
        broker_count=1,
    )
    decision = engine._evaluate_position_reconciliation(recovery, report)

    assert decision.safe_to_continue is True
    assert decision.requires_manual_resolution is False
    assert engine.ctx.position_reconciliation == decision
