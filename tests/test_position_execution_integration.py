from datetime import datetime

from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.position_execution_bridge import position_state_from_execution_result
from execution.position_runtime_service import PositionRuntimeService
from execution.position_state_store import SQLitePositionStateStore


def _result():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24300,
        action=ExecutionAction.BUY,
        quantity=50,
        limit_price=100.0,
        strategy_name="test",
        client_order_id="client-1",
        created_at=datetime(2026, 9, 5, 9, 15),
    )
    return ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        intent=intent,
        broker_order_id="broker-1",
        filled_quantity=50,
        average_fill_price=101.0,
        timestamp=datetime(2026, 9, 5, 9, 16),
    )


def test_successful_execution_becomes_canonical_open_position(tmp_path):
    result = _result()
    state = position_state_from_execution_result(result, stop_loss=90.0, target=120.0)

    assert state is not None
    assert state.client_order_id == "client-1"
    assert state.broker_order_id == "broker-1"
    assert state.quantity == 50
    assert state.entry_price == 101.0


def test_non_executed_result_does_not_create_position():
    result = _result()
    rejected = ExecutionResult(
        status=ExecutionStatus.REJECTED,
        intent=result.intent,
        reason="blocked",
    )
    assert position_state_from_execution_result(rejected) is None


def test_successful_execution_can_be_persisted_and_recovered(tmp_path):
    state = position_state_from_execution_result(_result(), stop_loss=90.0, target=120.0)
    with SQLitePositionStateStore(str(tmp_path / "positions.db")) as store:
        service = PositionRuntimeService(store)
        store.save(state)
        recovered = service.store.get("client-1")

    assert recovered == state
