from datetime import datetime
from types import SimpleNamespace

from execution.position_state import PositionStatus
from execution.position_state_adapter import broker_position_to_state, paper_position_to_state


def test_paper_position_maps_to_canonical_state():
    opened = datetime(2026, 9, 5, 9, 0)
    position = SimpleNamespace(
        closed=False,
        current_price=125.5,
        stop_loss=100.0,
        target=160.0,
        exit_time=None,
        order=SimpleNamespace(
            order_id="CID-1",
            broker_order_id="",
            symbol="NIFTY",
            option_type="CE",
            strike=25000,
            quantity=75,
            entry_price=120.0,
            order_time=opened,
        ),
    )

    state = paper_position_to_state(position)

    assert state.client_order_id == "CID-1"
    assert state.symbol == "NIFTY"
    assert state.option_type == "CE"
    assert state.strike == 25000
    assert state.quantity == 75
    assert state.status is PositionStatus.OPEN
    assert state.opened_at == opened
    assert state.closed_at is None


def test_closed_paper_position_maps_closed_timestamp():
    closed = datetime(2026, 9, 5, 10, 0)
    position = SimpleNamespace(
        closed=True,
        current_price=140.0,
        stop_loss=100.0,
        target=160.0,
        exit_time=closed,
        order=SimpleNamespace(
            order_id="CID-2",
            broker_order_id="BID-2",
            symbol="NIFTY",
            option_type="PE",
            strike=24900,
            quantity=75,
            entry_price=130.0,
            order_time=datetime(2026, 9, 5, 9, 30),
        ),
    )

    state = paper_position_to_state(position)
    assert state.status is PositionStatus.CLOSED
    assert state.broker_order_id == "BID-2"
    assert state.closed_at == closed


def test_broker_position_maps_provider_position_identity():
    position = SimpleNamespace(
        client_order_id="CID-3",
        broker_order_id="BID-3",
        symbol="NIFTY",
        option_type="CE",
        strike=25050,
        quantity=75,
        avg_price=145.25,
        current_price=151.0,
        status="OPEN",
    )

    state = broker_position_to_state(position)
    assert state.client_order_id == "CID-3"
    assert state.broker_order_id == "BID-3"
    assert state.entry_price == 145.25
    assert state.current_price == 151.0
    assert state.status is PositionStatus.OPEN


def test_broker_position_uses_position_id_fallback_and_unknown_status():
    position = SimpleNamespace(
        client_order_id="CID-4",
        position_id="POS-4",
        symbol="NIFTY",
        option_type="PE",
        strike=24950,
        quantity=75,
        avg_price=110.0,
        status="PARTIALLY FILLED",
    )

    state = broker_position_to_state(position)
    assert state.broker_order_id == "POS-4"
    assert state.status is PositionStatus.UNKNOWN
