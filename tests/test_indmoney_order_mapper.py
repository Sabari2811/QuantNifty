import pytest

from execution.execution_contract import ExecutionAction, OrderIntent
from execution.indmoney_order_mapper import build_indmoney_order_request
from execution.instrument_execution_resolver import ExecutionInstrument


@pytest.fixture
def intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=150,
        limit_price=125.5,
        strategy_name="TEST",
        client_order_id="qn-test-order-001",
        metadata={"expiry": "2026-09-10"},
    )


@pytest.fixture
def instrument():
    return ExecutionInstrument(
        security_id=123456,
        symbol="NIFTY",
        expiry="2026-09-10",
        strike=24000,
        option_type="CE",
        lot_units=75,
    )


def test_maps_canonical_buy_intent_to_documented_request(intent, instrument):
    request = build_indmoney_order_request(intent, instrument)

    assert request.as_dict() == {
        "txn_type": "BUY",
        "exchange": "NSE",
        "segment": "DERIVATIVE",
        "product": "MARGIN",
        "order_type": "LIMIT",
        "validity": "DAY",
        "security_id": "123456",
        "qty": 150,
        "algo_id": "99999",
        "limit_price": 125.5,
        "is_amo": False,
        "remarks": "qn-test-order-001",
    }


def test_maps_sell_action(intent, instrument):
    sell_intent = OrderIntent(
        symbol=intent.symbol,
        option_type=intent.option_type,
        strike=intent.strike,
        action=ExecutionAction.SELL,
        quantity=intent.quantity,
        limit_price=intent.limit_price,
        client_order_id=intent.client_order_id,
    )

    request = build_indmoney_order_request(sell_intent, instrument)

    assert request.txn_type == "SELL"


def test_rejects_quantity_not_multiple_of_resolved_lot(intent, instrument):
    invalid = OrderIntent(
        symbol=intent.symbol,
        option_type=intent.option_type,
        strike=intent.strike,
        action=intent.action,
        quantity=100,
        limit_price=intent.limit_price,
        client_order_id=intent.client_order_id,
    )

    with pytest.raises(ValueError, match="multiple of the resolved lot size"):
        build_indmoney_order_request(invalid, instrument)


def test_rejects_missing_client_order_id(intent, instrument):
    invalid = OrderIntent(
        symbol=intent.symbol,
        option_type=intent.option_type,
        strike=intent.strike,
        action=intent.action,
        quantity=intent.quantity,
        limit_price=intent.limit_price,
    )

    with pytest.raises(ValueError, match="client_order_id is required"):
        build_indmoney_order_request(invalid, instrument)


def test_rejects_missing_security_id(intent):
    invalid = ExecutionInstrument(
        security_id=0,
        symbol="NIFTY",
        expiry="2026-09-10",
        strike=24000,
        option_type="CE",
        lot_units=75,
    )

    with pytest.raises(ValueError, match="security_id must be positive"):
        build_indmoney_order_request(intent, invalid)


def test_rejects_non_limit_order(intent, instrument):
    with pytest.raises(ValueError, match="LIMIT orders only"):
        build_indmoney_order_request(intent, instrument, order_type="MARKET")


def test_allows_documented_intraday_derivative_product(intent, instrument):
    request = build_indmoney_order_request(
        intent,
        instrument,
        product="INTRADAY",
        validity="IOC",
        algo_id="custom-algo",
        is_amo=True,
    )

    assert request.product == "INTRADAY"
    assert request.validity == "IOC"
    assert request.algo_id == "custom-algo"
    assert request.is_amo is True
