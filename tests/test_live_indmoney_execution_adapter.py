from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionStatus, OrderIntent
from execution.indmoney_order_mapper import INDMoneyOrderRequest
from execution.instrument_execution_resolver import ExecutionInstrument
from execution.live_indmoney_execution_adapter import LiveINDMoneyExecutionAdapter


class FakeResolver:
    def resolve(self, intent):
        return ExecutionInstrument(
            security_id=823580,
            symbol=intent.symbol,
            expiry="2026-09-10",
            strike=intent.strike,
            option_type=intent.option_type,
            lot_units=75,
        )


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests = []

    def place_order(self, request):
        self.requests.append(request)
        if self.error:
            raise self.error
        return self.response


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


def test_build_request_uses_resolver_and_mapper():
    provider = FakeProvider()
    adapter = LiveINDMoneyExecutionAdapter(provider, FakeResolver())

    request = adapter.build_request(intent())

    assert isinstance(request, INDMoneyOrderRequest)
    assert request.security_id == "823580"
    assert request.qty == 75
    assert request.remarks == "qn-test-001"
    assert provider.requests == []


def test_execute_maps_provider_success_to_canonical_result():
    provider = FakeProvider({
        "status": "success",
        "data": {
            "order_id": "ORD-1",
            "order_status": "SUCCESS",
            "traded_qty": 75,
            "average_price": 120.25,
        },
    })
    adapter = LiveINDMoneyExecutionAdapter(provider, FakeResolver())

    result = adapter.execute(intent())

    assert result.status is ExecutionStatus.EXECUTED
    assert result.broker_order_id == "ORD-1"
    assert result.filled_quantity == 75
    assert len(provider.requests) == 1


def test_execute_provider_failure_maps_to_failed():
    provider = FakeProvider(error=RuntimeError("timeout"))
    adapter = LiveINDMoneyExecutionAdapter(provider, FakeResolver())

    result = adapter.execute(intent())

    assert result.status is ExecutionStatus.FAILED
    assert "timeout" in result.reason


def test_execute_mapping_failure_maps_to_failed():
    provider = FakeProvider({"status": "success", "data": {}})
    adapter = LiveINDMoneyExecutionAdapter(provider, FakeResolver())

    result = adapter.execute(intent())

    assert result.status is ExecutionStatus.FAILED
    assert "broker order ID" in result.reason
