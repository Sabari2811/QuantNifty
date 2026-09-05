from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from execution.position_runtime_service import PositionRuntimeService
from execution.position_state import PositionStatus
from execution.position_state_store import SQLitePositionStateStore
from paper_trading.broker import PaperBroker
from paper_trading.models import PaperOrder, PaperPosition


def _position(*, current_price=110.0, stop_loss=90.0, target=120.0, closed=False):
    order = PaperOrder(
        order_id="client-1",
        signal="BUY",
        option_type="CE",
        strike=24300,
        quantity=50,
        entry_price=100.0,
    )
    return PaperPosition(
        order=order,
        current_price=current_price,
        stop_loss=stop_loss,
        target=target,
        closed=closed,
        exit_time=datetime(2026, 9, 5, 10, 0) if closed else None,
    )


def test_runtime_service_persists_position_created_by_paper_broker(tmp_path: Path):
    broker = PaperBroker()
    position = _position()
    broker.portfolio.open_positions.append(position)

    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        state = service.persist_paper_position(broker.position)
        saved = store.get("client-1")

    assert saved == state
    assert state.status is PositionStatus.OPEN
    assert state.current_price == 110.0


def test_runtime_service_persists_closed_position_after_broker_close(tmp_path: Path):
    broker = PaperBroker()
    position = _position()
    broker.portfolio.open_positions.append(position)
    broker.close_position(position, 121.0, "TARGET")

    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        state = service.persist_paper_position(position)
        saved = store.get("client-1")

    assert saved == state
    assert state.status is PositionStatus.CLOSED
    assert state.closed_at == position.exit_time
