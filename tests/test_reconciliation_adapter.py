from dataclasses import dataclass

import pytest

from execution.reconciliation import ReconciliationStatus
from execution.reconciliation_adapter import (
    broker_position_snapshot,
    local_position_snapshot,
    reconcile_runtime_positions,
)


@dataclass
class FakeOrder:
    order_id: str = "client-1"
    symbol: str = "NIFTY"
    option_type: str = "CE"
    strike: float = 24000
    quantity: int = 75
    status: str = "OPEN"
    broker_order_id: str = "broker-1"


@dataclass
class FakePosition:
    order: FakeOrder
    closed: bool = False


def test_local_position_adapter_uses_order_identity_and_shape():
    snapshot = local_position_snapshot(FakePosition(FakeOrder()))

    assert snapshot.client_order_id == "client-1"
    assert snapshot.symbol == "NIFTY"
    assert snapshot.option_type == "CE"
    assert snapshot.strike == 24000
    assert snapshot.quantity == 75
    assert snapshot.status == "OPEN"
    assert snapshot.broker_order_id == "broker-1"


def test_closed_local_position_is_reconciled_as_closed():
    snapshot = local_position_snapshot(FakePosition(FakeOrder(), closed=True))

    assert snapshot.status == "CLOSED"


def test_local_position_without_order_identity_fails_closed():
    with pytest.raises(ValueError, match="order_id is required"):
        local_position_snapshot(FakePosition(FakeOrder(order_id="")))


def test_broker_adapter_requires_identity():
    with pytest.raises(ValueError, match="client/order identity"):
        broker_position_snapshot(type("BrokerPosition", (), {"symbol": "NIFTY", "option_type": "CE", "strike": 24000, "quantity": 75})())


def test_runtime_reconciliation_matches_adapted_positions():
    local = FakePosition(FakeOrder())
    broker = type(
        "BrokerPosition",
        (),
        {
            "client_order_id": "client-1",
            "symbol": "NIFTY",
            "option_type": "CE",
            "strike": 24000,
            "quantity": 75,
            "status": "OPEN",
            "broker_order_id": "broker-1",
        },
    )()

    report = reconcile_runtime_positions([local], [broker])

    assert report.status is ReconciliationStatus.MATCH
    assert report.safe_to_continue is True


def test_runtime_reconciliation_detects_quantity_mismatch():
    local = FakePosition(FakeOrder(quantity=75))
    broker = type(
        "BrokerPosition",
        (),
        {
            "client_order_id": "client-1",
            "symbol": "NIFTY",
            "option_type": "CE",
            "strike": 24000,
            "quantity": 150,
            "status": "OPEN",
            "broker_order_id": "broker-1",
        },
    )()

    report = reconcile_runtime_positions([local], [broker])

    assert report.status is ReconciliationStatus.MISMATCH
    assert report.issues[0].reason == "Quantity mismatch"


def test_unavailable_broker_positions_remain_unknown():
    report = reconcile_runtime_positions([FakePosition(FakeOrder())], None)

    assert report.status is ReconciliationStatus.UNKNOWN
    assert report.safe_to_continue is False
