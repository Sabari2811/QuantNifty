from datetime import datetime

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.position_execution_bridge import position_state_from_execution_result
from execution.position_state import PositionStatus


def _result(status=ExecutionStatus.EXECUTED, filled_quantity=50, avg_price=101.5):
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        action=ExecutionAction.BUY,
        quantity=50,
        limit_price=102.0,
        client_order_id="client-1",
        created_at=datetime(2026, 9, 5, 9, 15),
    )
    return ExecutionResult(
        status=status,
        intent=intent,
        broker_order_id="broker-1",
        filled_quantity=filled_quantity,
        average_fill_price=avg_price,
        timestamp=datetime(2026, 9, 5, 9, 15, 1),
    )


def test_successful_execution_creates_open_position_state():
    state = position_state_from_execution_result(
        _result(),
        current_price=103.0,
        stop_loss=90.0,
        target=120.0,
    )
    assert state is not None
    assert state.status is PositionStatus.OPEN
    assert state.client_order_id == "client-1"
    assert state.broker_order_id == "broker-1"
    assert state.quantity == 50
    assert state.entry_price == 101.5
    assert state.current_price == 103.0


def test_execution_bridge_uses_limit_price_when_average_fill_missing():
    state = position_state_from_execution_result(_result(avg_price=None))
    assert state is not None
    assert state.entry_price == 102.0
    assert state.current_price == 102.0


def test_non_executed_result_does_not_create_position_state():
    assert position_state_from_execution_result(
        _result(status=ExecutionStatus.REJECTED)
    ) is None


def test_partial_filled_quantity_is_preserved_for_position_state():
    state = position_state_from_execution_result(_result(filled_quantity=20))
    assert state is not None
    assert state.quantity == 20
