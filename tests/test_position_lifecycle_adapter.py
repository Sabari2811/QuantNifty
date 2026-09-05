from dataclasses import dataclass

import pytest

from execution.position_lifecycle import PositionLifecycleAction
from execution.position_lifecycle_adapter import (
    evaluate_paper_position_lifecycle,
    should_close_paper_position,
)


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


def test_adapter_maps_paper_position_and_holds():
    result = evaluate_paper_position_lifecycle(Position())
    assert result.lifecycle.action is PositionLifecycleAction.HOLD
    assert result.position.current_price == 110.0


def test_adapter_maps_stop_loss():
    result = evaluate_paper_position_lifecycle(Position(current_price=89.0))
    assert result.lifecycle.action is PositionLifecycleAction.CLOSE_STOP_LOSS


def test_adapter_maps_target():
    result = evaluate_paper_position_lifecycle(Position(current_price=121.0))
    assert result.lifecycle.action is PositionLifecycleAction.CLOSE_TARGET


def test_adapter_preserves_trailing_stop_precedence():
    result = evaluate_paper_position_lifecycle(
        Position(current_price=94.0, trailing_stop=95.0, stop_loss=90.0)
    )
    assert result.lifecycle.action is PositionLifecycleAction.CLOSE_STOP_LOSS
    assert "Trailing" in result.lifecycle.reason


def test_adapter_manual_close():
    assert should_close_paper_position(Position(), manual_close=True) is True


def test_adapter_does_not_mutate_legacy_position():
    position = Position(current_price=110.0)
    evaluate_paper_position_lifecycle(position, current_price=121.0)
    assert position.closed is False
    assert position.current_price == 110.0


def test_adapter_rejects_invalid_position():
    with pytest.raises(ValueError, match="Position is missing its order"):
        evaluate_paper_position_lifecycle(object())
