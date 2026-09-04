from datetime import datetime

import pytest

from execution.execution_contract import (
    ExecutionAction,
    ExecutionStatus,
    ExecutionResult,
    OrderIntent,
)


def make_intent(**overrides):
    values = {
        "symbol": "NIFTY",
        "option_type": "CE",
        "strike": 24000,
        "action": ExecutionAction.BUY,
        "quantity": 50,
        "limit_price": 125.5,
    }
    values.update(overrides)
    return OrderIntent(**values)


def test_order_intent_is_broker_neutral_and_typed():
    created_at = datetime.now()
    intent = make_intent(
        strategy_name="TEST_STRATEGY",
        source="decision",
        client_order_id="qn-test-001",
        created_at=created_at,
        metadata={"confidence": 0.82},
    )

    assert intent.symbol == "NIFTY"
    assert intent.option_type == "CE"
    assert intent.strike == 24000
    assert intent.action is ExecutionAction.BUY
    assert intent.quantity == 50
    assert intent.limit_price == 125.5
    assert intent.strategy_name == "TEST_STRATEGY"
    assert intent.client_order_id == "qn-test-001"
    assert intent.created_at is created_at
    assert intent.metadata == {"confidence": 0.82}


def test_order_intent_rejects_invalid_shape():
    with pytest.raises(ValueError):
        make_intent(symbol="")

    with pytest.raises(ValueError):
        make_intent(option_type="")

    with pytest.raises(ValueError):
        make_intent(strike=0)

    with pytest.raises(ValueError):
        make_intent(quantity=0)

    with pytest.raises(ValueError):
        make_intent(limit_price=-1)


def test_execution_result_distinguishes_terminal_and_successful_states():
    intent = make_intent()

    executed = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        intent=intent,
        broker_order_id="broker-1",
        filled_quantity=50,
        average_fill_price=126.0,
    )
    rejected = ExecutionResult(
        status=ExecutionStatus.REJECTED,
        intent=intent,
        reason="Rejected by broker.",
    )
    unknown = ExecutionResult(
        status=ExecutionStatus.UNKNOWN,
        intent=intent,
    )

    assert executed.successful is True
    assert executed.terminal is True
    assert rejected.successful is False
    assert rejected.terminal is True
    assert unknown.successful is False
    assert unknown.terminal is False


def test_execution_result_preserves_partial_fill_information_without_marking_success():
    intent = make_intent(quantity=100)
    result = ExecutionResult(
        status=ExecutionStatus.SUBMITTED,
        intent=intent,
        broker_order_id="broker-2",
        filled_quantity=40,
        average_fill_price=127.25,
        reason="40 of 100 filled; remainder pending.",
    )

    assert result.successful is False
    assert result.terminal is False
    assert result.filled_quantity == 40
    assert result.average_fill_price == 127.25
