from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionStatus, OrderIntent
from execution.live_indmoney_execution_adapter import LiveINDMoneyExecutionAdapter
from execution.instrument_execution_resolver import ExecutionInstrument


class FakeResolver:
    def __init__(self, instrument=None):
        self.instrument = instrument or ExecutionInstrument(
            security_id=823580,
            symbol="NIFTY",
            expiry="2026-09-10",
            strike=25000,
            option_type="CE",
            lot_units=75,
        )
        self.calls = []

    def resolve(self, intent):
        self.calls.append(intent)
        return self.instrument


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def place_order(self, request):
        self.calls.append(request)
        if self.error is not None:
            raise self.error
        return self.response


def make_intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.5,
        client_order_id="qn-runtime-001",
        metadata={"expiry": "2026-09-10"},
    )


def test_runtime_adapter_build_request_resolves_authoritative_instrument_once():
    resolver = FakeResolver()
    provider = FakeProvider()
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    request = adapter.build_request(make_intent())

    assert len(resolver.calls) == 1
    assert request.security_id == "823580"
    assert request.qty == 75
    assert provider.calls == []


def test_runtime_adapter_success_returns_canonical_result():
    resolver = FakeResolver()
    provider = FakeProvider({
        "status": "success",
        "data": {
            "order_id": "ORD-100",
            "order_status": "SUCCESS",
            "traded_qty": 75,
            "average_price": 121.0,
        },
    })
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(make_intent())

    assert result.status is ExecutionStatus.EXECUTED
    assert result.broker_order_id == "ORD-100"
    assert result.filled_quantity == 75
    assert result.average_fill_price == 121.0
    assert len(provider.calls) == 1
    assert provider.calls[0].remarks == "qn-runtime-001"


def test_runtime_adapter_submission_failure_fails_closed():
    resolver = FakeResolver()
    provider = FakeProvider(error=TimeoutError("provider timeout"))
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(make_intent())

    assert result.status is ExecutionStatus.FAILED
    assert "provider timeout" in result.reason
    assert result.broker_order_id == ""


def test_runtime_adapter_malformed_response_fails_closed():
    resolver = FakeResolver()
    provider = FakeProvider({"status": "success"})
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(make_intent())

    assert result.status is ExecutionStatus.FAILED
    assert "response mapping failed" in result.reason
    assert len(provider.calls) == 1


def test_runtime_adapter_does_not_accept_missing_intent():
    adapter = LiveINDMoneyExecutionAdapter(FakeProvider(), FakeResolver())

    try:
        adapter.execute(None)
    except ValueError as exc:
        assert str(exc) == "Order intent is required"
    else:
        raise AssertionError("Expected ValueError")
