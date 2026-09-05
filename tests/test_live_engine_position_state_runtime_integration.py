from datetime import datetime

from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionStatus
from execution.position_state_store import SQLitePositionStateStore


class FakeProvider:
    def connect(self):
        return True


class FakeStore:
    def __init__(self):
        self.saved = []

    def save(self, state):
        self.saved.append(state)
        return state


def test_live_engine_position_service_is_initialized_from_store():
    from engine.live_engine import LiveEngine

    engine = object.__new__(LiveEngine)
    engine.position_runtime_service = PositionRuntimeService(FakeStore())
    assert isinstance(engine.position_runtime_service, PositionRuntimeService)


def test_position_service_persists_canonical_open_state():
    from dataclasses import dataclass, field
    from execution.position_state import PositionState

    @dataclass
    class Order:
        order_id: str = "client-1"
        broker_order_id: str = "broker-1"
        symbol: str = "NIFTY"
        option_type: str = "CE"
        strike: float = 24300
        quantity: int = 50
        entry_price: float = 100.0
        order_time: datetime = datetime(2026, 9, 5, 9, 15)

    @dataclass
    class Position:
        order: Order = field(default_factory=Order)
        current_price: float = 110.0
        stop_loss: float = 90.0
        target: float = 120.0
        trailing_stop: float | None = None
        closed: bool = False
        exit_time: datetime | None = None

    store = FakeStore()
    service = PositionRuntimeService(store)
    state = service.persist_paper_position(Position())

    assert state.client_order_id == "client-1"
    assert state.broker_order_id == "broker-1"
    assert state.symbol == "NIFTY"
    assert state.option_type == "CE"
    assert isinstance(state, PositionState)
    assert state.status is PositionStatus.OPEN
    assert store.saved == [state]
