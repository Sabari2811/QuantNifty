from types import SimpleNamespace

from execution.execution_contract import ExecutionStatus, OrderIntent, ExecutionAction
from execution.paper_execution_adapter import PaperExecutionAdapter


class FakeBroker:
    def __init__(self, result):
        self.result = result

    def execute(self, decision):
        return self.result


def intent():
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        client_order_id="client-1",
    )


def test_paper_execution_adapter_maps_success_to_canonical_result():
    position = SimpleNamespace(order=SimpleNamespace(order_id="paper-1"))
    adapter = PaperExecutionAdapter(FakeBroker(position))

    result = adapter.execute(intent(), SimpleNamespace())

    assert result.status is ExecutionStatus.EXECUTED
    assert result.successful is True
    assert result.broker_order_id == "paper-1"
    assert result.filled_quantity == 75
    assert result.average_fill_price == 100


def test_paper_execution_adapter_maps_broker_rejection():
    adapter = PaperExecutionAdapter(FakeBroker(None))

    result = adapter.execute(intent(), SimpleNamespace())

    assert result.status is ExecutionStatus.REJECTED
    assert result.successful is False
    assert result.terminal is True
    assert result.reason == "Paper broker rejected execution"


def test_paper_execution_adapter_requires_client_order_identity():
    adapter = PaperExecutionAdapter(FakeBroker(None))
    invalid = intent()
    object.__setattr__(invalid, "client_order_id", "")

    result = adapter.execute(invalid, SimpleNamespace())

    assert result.status is ExecutionStatus.REJECTED
    assert result.reason == "client_order_id is required"
