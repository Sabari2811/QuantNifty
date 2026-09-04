from datetime import datetime

import pytest

from decision.models.option_contract import OptionContract
from execution.execution_contract import ExecutionAction, OrderIntent, ExecutionStatus
from execution.indmoney_execution_result_mapper import map_indmoney_execution_result


@pytest.fixture
def intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.5,
        strategy_name="TEST",
        client_order_id="qn-test-001",
        metadata={"expiry": "2026-09-10"},
    )


def test_success_maps_to_executed(intent):
    result = map_indmoney_execution_result(
        intent,
        {"status": "success", "data": {"order_id": "ORD-1", "order_status": "SUCCESS", "traded_qty": 75, "average_price": 120.25}},
    )
    assert result.status is ExecutionStatus.EXECUTED
    assert result.broker_order_id == "ORD-1"
    assert result.filled_quantity == 75
    assert result.average_fill_price == 120.25
    assert result.raw["data"]["order_id"] == "ORD-1"


def test_pending_maps_to_submitted(intent):
    result = map_indmoney_execution_result(intent, {"status": "success", "data": {"order_id": "ORD-2", "order_status": "O-PENDING"}})
    assert result.status is ExecutionStatus.SUBMITTED
    assert result.broker_order_id == "ORD-2"


def test_partial_fill_maps_to_submitted(intent):
    result = map_indmoney_execution_result(intent, {"status": "success", "data": {"order_id": "ORD-3", "order_status": "PARTIALLY FILLED", "traded_qty": 25}})
    assert result.status is ExecutionStatus.SUBMITTED
    assert result.filled_quantity == 25


def test_rejected_maps_to_rejected(intent):
    result = map_indmoney_execution_result(intent, {"status": "success", "data": {"order_id": "ORD-4", "order_status": "CANCELLED", "message": "cancelled by provider"}})
    assert result.status is ExecutionStatus.REJECTED
    assert result.reason == "cancelled by provider"


def test_unknown_status_maps_to_unknown(intent):
    result = map_indmoney_execution_result(intent, {"status": "success", "data": {"order_id": "ORD-5", "order_status": "SOMETHING_NEW"}})
    assert result.status is ExecutionStatus.UNKNOWN


def test_missing_order_id_fails_closed(intent):
    result = map_indmoney_execution_result(intent, {"status": "success", "data": {"order_status": "SUCCESS"}})
    assert result.status is ExecutionStatus.FAILED
    assert "broker order ID" in result.reason


def test_missing_data_rejected_as_malformed(intent):
    with pytest.raises(ValueError, match="response data is missing"):
        map_indmoney_execution_result(intent, {"status": "success"})


def test_preserves_explicit_timestamp(intent):
    timestamp = datetime(2026, 9, 4, 10, 30, 0)
    result = map_indmoney_execution_result(
        intent,
        {"status": "success", "data": {"order_id": "ORD-6", "order_status": "SUCCESS"}},
        timestamp=timestamp,
    )
    assert result.timestamp == timestamp
