from types import SimpleNamespace

from execution.execution_contract import ExecutionAction, ExecutionStatus, OrderIntent
from execution.instrument_execution_resolver import ExecutionInstrument
from execution.live_indmoney_execution_adapter import LiveINDMoneyExecutionAdapter


class FakeResolver:
    def __init__(self, instrument):
        self.instrument = instrument
        self.calls = 0
        self.intent = None

    def resolve(self, intent):
        self.calls += 1
        self.intent = intent
        return self.instrument


class FakeProvider:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = 0
        self.request = None

    def place_order(self, request):
        self.calls += 1
        self.request = request
        if self.error is not None:
            raise self.error
        return self.response


def build_intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.5,
        strategy_name="TEST",
        client_order_id="qn-live-001",
        metadata={"expiry": "2026-09-10"},
    )


def build_instrument():
    return ExecutionInstrument(
        security_id=823580,
        symbol="NIFTY",
        expiry="2026-09-10",
        strike=25000,
        option_type="CE",
        lot_units=75,
    )


def test_adapter_composes_resolver_provider_and_result_mapper():
    intent = build_intent()
    resolver = FakeResolver(build_instrument())
    provider = FakeProvider(
        response={
            "status": "success",
            "data": {
                "order_id": "ORD-100",
                "order_status": "SUCCESS",
                "traded_qty": 75,
                "average_price": 120.25,
            },
        }
    )
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(intent)

    assert resolver.calls == 1
    assert provider.calls == 1
    assert result.status is ExecutionStatus.EXECUTED
    assert result.broker_order_id == "ORD-100"
    assert result.filled_quantity == 75
    assert result.average_fill_price == 120.25
    assert provider.request.security_id == "823580"
    assert provider.request.qty == 75
    assert provider.request.remarks == "qn-live-001"


def test_adapter_returns_failed_when_submission_raises():
    intent = build_intent()
    resolver = FakeResolver(build_instrument())
    provider = FakeProvider(error=RuntimeError("provider unavailable"))
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(intent)

    assert result.status is ExecutionStatus.FAILED
    assert "provider unavailable" in result.reason
    assert provider.calls == 1


def test_adapter_returns_failed_for_malformed_provider_response():
    intent = build_intent()
    resolver = FakeResolver(build_instrument())
    provider = FakeProvider(response={"status": "success"})
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    result = adapter.execute(intent)

    assert result.status is ExecutionStatus.FAILED
    assert "response data is missing" in result.reason


def test_adapter_does_not_place_order_when_instrument_resolution_fails():
    intent = build_intent()
    provider = FakeProvider(response={"status": "success", "data": {"order_id": "ORD-101"}})

    class FailingResolver:
        def resolve(self, intent):
            raise LookupError("contract not found")

    adapter = LiveINDMoneyExecutionAdapter(provider, FailingResolver())

    result = adapter.execute(intent)

    assert result.status is ExecutionStatus.FAILED
    assert "contract not found" in result.reason
    assert provider.calls == 0


def test_build_request_is_side_effect_free():
    intent = build_intent()
    resolver = FakeResolver(build_instrument())
    provider = FakeProvider()
    adapter = LiveINDMoneyExecutionAdapter(provider, resolver)

    request = adapter.build_request(intent)

    assert request.security_id == "823580"
    assert request.qty == 75
    assert provider.calls == 0
    assert resolver.calls == 1
