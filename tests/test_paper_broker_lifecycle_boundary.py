from types import SimpleNamespace

from paper_trading.broker import PaperBroker
from paper_trading.models import PaperOrder, PaperPosition


def _position(*, current_price=110.0, stop_loss=90.0, target=120.0):
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
    )


def _chain(price):
    return [{"strike": 24300, "option_type": "CE", "ltp": price}]


def test_paper_broker_closes_on_target_through_existing_runtime_boundary(monkeypatch):
    broker = PaperBroker()
    position = _position()
    broker.portfolio.open_positions.append(position)

    broker.update_positions(_chain(121.0))

    assert position.closed is True
    assert position.exit_price == 121.0


def test_paper_broker_closes_on_stop_loss_through_existing_runtime_boundary(monkeypatch):
    broker = PaperBroker()
    position = _position()
    broker.portfolio.open_positions.append(position)

    broker.update_positions(_chain(89.0))

    assert position.closed is True
    assert position.exit_price == 89.0


def test_paper_broker_hold_path_remains_open():
    broker = PaperBroker()
    position = _position()
    broker.portfolio.open_positions.append(position)

    broker.update_positions(_chain(110.0))

    assert position.closed is False
    assert position.current_price == 110.0
