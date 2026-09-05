from datetime import datetime

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.position_execution_bridge import position_state_from_execution_result
from execution.position_state import PositionStatus


def _result(status=ExecutionStatus.EXECUTED, filled_quantity=50, average_fill_price=101.5):
    created = datetime(2026, 9, 5, 9, 15)
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        action=ExecutionAction.BUY,
        quantity=50,
        limit_price=100.0,
        client_order_id="client-1",
        created_at=created,
    )
    return ExecutionResult(
        status=status,
        intent=intent,
        broker_order_id="broker-1",
        filled_quantity=filled_quantity,
        average_fill_price=average_fill_price,
        timestamp=created,
    )


def test_successful_execution_creates_open_position():
    state = position_state_from_execution_result(
        _result(),
        current_price=102.0,
        stop_loss=95.0,
        target=115.0,
    )
    assert state is not None
    assert state.status is PositionStatus.OPEN
    assert state.client_order_id == "client-1"
    assert state.broker_order_id == "broker-1"
    assert state.quantity == 50
    assert state.entry_price == 101.5
    assert state.current_price == 102.0
    assert state.stop_loss == 95.0
    assert state.target == 115.0


def test_successful_execution_uses_limit_price_when_fill_price_missing():
    state = position_state_from_execution_result(_result(average_fill_price=None))
    assert state is not None
    assert state.entry_price == 100.0
    assert state.current_price == 100.0


def test_zero_filled_quantity_falls_back_to_intent_quantity():
    state = position_state_from_execution_result(_result(filled_quantity=0))
    assert state is not None
    assert state.quantity == 50


def test_non_terminal_success_is_not_a_position():
    assert position_state_from_execution_result(_result(ExecutionStatus.SUBMITTED)) is None
    assert position_state_from_execution_result(_result(ExecutionStatus.UNKNOWN)) is None
    assert position_state_from_execution_result(_result(ExecutionStatus.REJECTED)) is None
    assert position_state_from_execution_result(None) is None
