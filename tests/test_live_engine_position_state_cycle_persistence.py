from dataclasses import dataclass, field
from datetime import datetime

from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionStatus


class FakeStore:
    def __init__(self):
        self.saved = []

    def save(self, state):
        self.saved.append(state)
        return state


@dataclass
class Order:
    order_id: str = "client-1"
    broker_order_id: str = "broker-1"
    symbol: str = "NIFTY"
    option_type: str = "CE"
    strike: float = 24300
    quantity: int = 50
    entry_price: float = 100.0
    order_time: datetime = field(default_factory=lambda: datetime(2026, 9, 5, 9, 15))


@dataclass
class Position:
    order: Order = field(default_factory=Order)
    current_price: float = 110.0
    stop_loss: float = 90.0
    target: float = 120.0
    trailing_stop: float | None = None
    closed: bool = False
    exit_time: datetime | None = None


class Broker:
    def __init__(self, position):
        self.portfolio = type("Portfolio", (), {"open_positions": [position]})()
        self._last_trade = None

    @property
    def last_trade(self):
        return self._last_trade


def test_live_engine_persists_open_positions_each_cycle():
    from engine.live_engine import LiveEngine

    store = FakeStore()
    engine = object.__new__(LiveEngine)
    engine.position_runtime_service = PositionRuntimeService(store)
    engine.paper_broker = Broker(Position())

    engine._persist_position_runtime_state()

    assert len(store.saved) == 1
    assert store.saved[0].status is PositionStatus.OPEN
    assert store.saved[0].client_order_id == "client-1"


def test_live_engine_persists_closed_last_trade():
    from engine.live_engine import LiveEngine

    position = Position(closed=True, exit_time=datetime(2026, 9, 5, 9, 30), current_price=120.0)
    store = FakeStore()
    engine = object.__new__(LiveEngine)
    engine.position_runtime_service = PositionRuntimeService(store)
    engine.paper_broker = Broker(position)
    engine.paper_broker.portfolio.open_positions = []
    engine.paper_broker._last_trade = position

    engine._persist_position_runtime_state()

    assert len(store.saved) == 1
    assert store.saved[0].status is PositionStatus.CLOSED
    assert store.saved[0].closed_at == position.exit_time
