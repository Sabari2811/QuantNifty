from datetime import datetime

from execution.position_state import PositionState, PositionStatus
from execution.position_state_store import SQLitePositionStateStore


def _position(**overrides):
    values = dict(
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
        trailing_stop=95.0,
        status=PositionStatus.OPEN,
        opened_at=datetime(2026, 9, 5, 9, 15),
    )
    values.update(overrides)
    return PositionState(**values)


def test_store_round_trips_position(tmp_path):
    path = tmp_path / "positions.db"
    position = _position()
    with SQLitePositionStateStore(str(path)) as store:
        store.save(position)
        restored = store.get("client-1")

    assert restored == position


def test_store_upserts_same_canonical_identity(tmp_path):
    path = tmp_path / "positions.db"
    with SQLitePositionStateStore(str(path)) as store:
        store.save(_position(current_price=110.0))
        store.save(_position(current_price=115.0))
        restored = store.get("client-1")

    assert restored is not None
    assert restored.current_price == 115.0


def test_store_returns_only_open_positions(tmp_path):
    path = tmp_path / "positions.db"
    closed = _position(
        client_order_id="client-2",
        status=PositionStatus.CLOSED,
        closed_at=datetime(2026, 9, 5, 10, 0),
    )
    with SQLitePositionStateStore(str(path)) as store:
        store.save(_position())
        store.save(closed)
        open_positions = store.open_positions()

    assert open_positions == (_position(),)


def test_store_missing_position_returns_none(tmp_path):
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        assert store.get("missing") is None
