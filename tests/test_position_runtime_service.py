from dataclasses import dataclass
from datetime import datetime

from execution.position_lifecycle import PositionLifecycleAction, PositionLifecycleDecision
from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionStatus
from execution.position_state_store import SQLitePositionStateStore


@dataclass
class Order:
    order_id: str = "client-1"
    broker_order_id: str = "broker-1"
    symbol: str = "NIFTY"
    option_type: str = "CE"
    strike: float = 24300
    quantity: int = 50
    entry_price: float = 100.0
    order_time: object = None


@dataclass
class Position:
    order: Order
    current_price: float = 110.0
    stop_loss: float = 90.0
    target: float = 120.0
    trailing_stop: float | None = None
    closed: bool = False
    exit_time: object = None


def test_service_persists_paper_position(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        state = service.persist_paper_position(Position())
        assert store.get("client-1") == state
        assert state.status is PositionStatus.OPEN


def test_service_evaluates_without_mutation(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        position = Position(current_price=121.0)
        result = service.evaluate_paper_position(position)

    assert result.lifecycle.action is PositionLifecycleAction.CLOSE_TARGET
    assert position.closed is False


def test_service_persists_closed_position_after_lifecycle(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        position = Position(current_price=121.0, closed=True, exit_time=datetime(2026, 9, 5, 10, 0))
        decision = PositionLifecycleDecision(
            PositionLifecycleAction.CLOSE_TARGET,
            "Target reached.",
        )
        state = service.persist_after_lifecycle(position, decision)

    assert state.status is PositionStatus.CLOSED
    assert state.closed_at == position.exit_time


def test_service_persists_hold_as_open_state(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        position = Position(current_price=110.0)
        decision = PositionLifecycleDecision(PositionLifecycleAction.HOLD, "No close condition reached.")
        state = service.persist_after_lifecycle(position, decision)

    assert state.status is PositionStatus.OPEN


def test_service_requires_store():
    try:
        PositionRuntimeService(None)
    except ValueError as exc:
        assert str(exc) == "Position state store is required"
    else:
        raise AssertionError("Expected ValueError")
