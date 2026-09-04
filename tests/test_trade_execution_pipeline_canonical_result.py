from types import SimpleNamespace

from core.runtime_context import RuntimeContext
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.trade_execution_pipeline import TradeExecutionPipeline


class FakePortfolioEngine:
    portfolio = SimpleNamespace(open_positions=[], invested_amount=0, capital=500000)


class FakeJournal:
    def summary(self):
        return {"trades": 0}


class FakeBroker:
    def __init__(self):
        self.portfolio_engine = FakePortfolioEngine()
        self.position = None
        self.last_trade = None
        self.journal = FakeJournal()
        self.execute_called = 0

    def execute(self, decision):
        self.execute_called += 1
        self.position = SimpleNamespace(order=SimpleNamespace(order_id="paper-1"))
        self.last_trade = decision.trade
        return self.position


class FakeRiskManager:
    state = "TEST_RISK_STATE"

    def validate(self, broker, decision, context=None):
        return True, ""


class FakeAdapter:
    def __init__(self, result):
        self.result = result
        self.calls = 0

    def execute(self, intent, decision):
        self.calls += 1
        return self.result


def build_context():
    ctx = RuntimeContext()
    ctx.decision = SimpleNamespace(
        valid=True,
        signal=SimpleNamespace(name="BUY CALL"),
        strategy_name="TEST",
        trade=SimpleNamespace(
            symbol="NIFTY",
            option_type="CE",
            strike=24000,
            entry=100,
            execution=SimpleNamespace(lot_size=75, lots=1),
        ),
    )
    ctx.execution_intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        strategy_name="TEST",
        client_order_id="client-1",
    )
    return ctx


def test_pipeline_persists_canonical_execution_result_and_lifecycle():
    broker = FakeBroker()
    result = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        intent=build_context().execution_intent,
        broker_order_id="paper-1",
        filled_quantity=75,
        average_fill_price=100,
    )
    adapter = FakeAdapter(result)
    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=FakeRiskManager(),
        execution_adapter=adapter,
    )

    ctx = build_context()
    pipeline.execute(ctx)

    assert adapter.calls == 1
    assert broker.execute_called == 0
    assert ctx.execution_result is result
    assert ctx.execution_lifecycle == "EXECUTE"
    assert ctx.trade_status == "EXECUTED"


def test_pipeline_persists_rejected_canonical_execution_result():
    broker = FakeBroker()
    result = ExecutionResult(
        status=ExecutionStatus.REJECTED,
        intent=build_context().execution_intent,
        reason="Paper broker rejected execution",
    )
    adapter = FakeAdapter(result)
    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=FakeRiskManager(),
        execution_adapter=adapter,
    )

    ctx = build_context()
    pipeline.execute(ctx)

    assert broker.execute_called == 0
    assert ctx.execution_result is result
    assert ctx.execution_lifecycle == "DO_NOT_RETRY"
    assert ctx.trade_status == "REJECTED"
    assert ctx.trade_block_reason == "Paper broker rejected execution"
