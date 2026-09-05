from dataclasses import dataclass, field
from datetime import datetime

from execution.position_lifecycle import PositionLifecycleAction
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
    order: Order = field(default_factory=Order)
    current_price: float = 110.0
    stop_loss: float = 90.0
    target: float = 120.0
    trailing_stop: float | None = None
    closed: bool = False
    exit_time: object = None


def test_target_lifecycle_is_persisted_as_closed_state(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        open_position = Position(current_price=121.0)
        lifecycle = service.evaluate_paper_position(open_position)
        assert lifecycle.lifecycle.action is PositionLifecycleAction.CLOSE_TARGET

        closed_position = Position(
            current_price=121.0,
            closed=True,
            exit_time=datetime(2026, 9, 5, 10, 0),
        )
        state = service.persist_after_lifecycle(closed_position, lifecycle.lifecycle)

    restored = SQLitePositionStateStore(str(tmp_path / "positions.db"))
    try:
        saved = restored.get("client-1")
    finally:
        restored.close()
    assert saved == state
    assert saved.status is PositionStatus.CLOSED


def test_hold_lifecycle_is_persisted_as_open_state(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        position = Position(current_price=110.0)
        lifecycle = service.evaluate_paper_position(position)
        state = service.persist_after_lifecycle(position, lifecycle.lifecycle)
        saved = store.get("client-1")

    assert lifecycle.lifecycle.action is PositionLifecycleAction.HOLD
    assert saved == state
    assert saved.status is PositionStatus.OPEN
