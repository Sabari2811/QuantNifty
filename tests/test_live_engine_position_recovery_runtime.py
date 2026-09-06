from datetime import datetime

from engine.live_engine import LiveEngine
from execution.position_recovery_runtime import PositionRecoveryRuntimeDecision
from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionState, PositionStatus


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


def test_live_engine_recovers_persisted_open_positions_without_mutating_broker_state():
    engine = object.__new__(LiveEngine)
    engine.ctx = type("Context", (), {})()
    engine.position_runtime_service = PositionRuntimeService(FakeStore((_open_position(),)))
    engine.paper_broker = type("Broker", (), {"position": None})()

    decision = engine._recover_position_runtime_state()

    assert isinstance(decision, PositionRecoveryRuntimeDecision)
    assert decision.safe_to_continue is True
    assert decision.positions == (_open_position(),)
    assert engine.paper_broker.position is None
    assert engine.ctx.position_recovery == decision


def test_live_engine_position_recovery_is_explicitly_blocked_without_store():
    engine = object.__new__(LiveEngine)
    engine.ctx = type("Context", (), {})()
    engine.position_runtime_service = None

    decision = engine._recover_position_runtime_state()

    assert decision.safe_to_continue is False
    assert decision.positions == ()
    assert engine.ctx.position_recovery == decision
