from datetime import datetime

import pytest

from execution.position_state import PositionState, PositionStatus


def make_position(**overrides):
    values = {
        "client_order_id": "client-1",
        "broker_order_id": "broker-1",
        "symbol": "NIFTY",
        "option_type": "CE",
        "strike": 25000,
        "quantity": 75,
        "entry_price": 100.0,
        "current_price": 105.0,
        "stop_loss": 80.0,
        "target": 140.0,
    }
    values.update(overrides)
    return PositionState(**values)


def test_open_position_preserves_canonical_identity_and_levels():
    position = make_position()
    assert position.client_order_id == "client-1"
    assert position.broker_order_id == "broker-1"
    assert position.status is PositionStatus.OPEN
    assert position.stop_loss == 80.0
    assert position.target == 140.0


def test_closed_position_requires_closed_timestamp():
    with pytest.raises(ValueError, match="closed_at is required"):
        make_position(status=PositionStatus.CLOSED)

    closed_at = datetime.now()
    position = make_position(status=PositionStatus.CLOSED, closed_at=closed_at)
    assert position.closed_at == closed_at


def test_open_position_cannot_have_closed_timestamp():
    with pytest.raises(ValueError, match="closed_at is not allowed"):
        make_position(closed_at=datetime.now())


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("client_order_id", "", "client_order_id is required"),
        ("symbol", "", "symbol is required"),
        ("option_type", "", "option_type is required"),
        ("strike", 0, "strike must be positive"),
        ("quantity", 0, "quantity must be positive"),
        ("entry_price", -1, "entry_price must be non-negative"),
        ("current_price", -1, "current_price must be non-negative"),
        ("stop_loss", -1, "stop_loss must be non-negative"),
        ("target", -1, "target must be non-negative"),
        ("trailing_stop", -1, "trailing_stop must be non-negative"),
    ],
)
def test_position_state_rejects_invalid_values(field, value, reason):
    with pytest.raises(ValueError, match=reason):
        make_position(**{field: value})


def test_trailing_stop_is_optional():
    position = make_position(trailing_stop=95.0)
    assert position.trailing_stop == 95.0
