from datetime import datetime

import pytest

from execution.position_lifecycle import (
    PositionLifecycleAction,
    evaluate_position_lifecycle,
)
from execution.position_state import PositionState, PositionStatus


def position(**overrides):
    values = dict(
        client_order_id="cid-1",
        broker_order_id="bid-1",
        symbol="NIFTY",
        option_type="CE",
        strike=24500,
        quantity=50,
        entry_price=100,
        current_price=110,
        stop_loss=90,
        target=130,
        opened_at=datetime.now(),
    )
    values.update(overrides)
    return PositionState(**values)


def test_hold_when_no_close_condition():
    result = evaluate_position_lifecycle(position(), current_price=110)
    assert result.action is PositionLifecycleAction.HOLD


def test_stop_loss_closes_position():
    result = evaluate_position_lifecycle(position(), current_price=90)
    assert result.action is PositionLifecycleAction.CLOSE_STOP_LOSS
    assert "Stop loss" in result.reason


def test_target_closes_position():
    result = evaluate_position_lifecycle(position(), current_price=130)
    assert result.action is PositionLifecycleAction.CLOSE_TARGET


def test_trailing_stop_takes_precedence_over_static_stop_when_reached():
    result = evaluate_position_lifecycle(
        position(stop_loss=90, trailing_stop=105),
        current_price=105,
    )
    assert result.action is PositionLifecycleAction.CLOSE_STOP_LOSS
    assert "Trailing stop" in result.reason


def test_manual_close_takes_precedence():
    result = evaluate_position_lifecycle(position(), current_price=110, manual_close=True)
    assert result.action is PositionLifecycleAction.CLOSE_MANUAL


def test_closed_position_is_not_reopened():
    result = evaluate_position_lifecycle(
        position(status=PositionStatus.CLOSED, closed_at=datetime.now()),
        current_price=80,
    )
    assert result.action is PositionLifecycleAction.HOLD


def test_default_current_price_uses_position_state():
    result = evaluate_position_lifecycle(position(current_price=130))
    assert result.action is PositionLifecycleAction.CLOSE_TARGET


def test_negative_current_price_rejected():
    with pytest.raises(ValueError, match="current_price"):
        evaluate_position_lifecycle(position(), current_price=-1)
