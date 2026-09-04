from types import SimpleNamespace

from core.runtime_context import RuntimeContext
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_audit_store import SQLiteExecutionAuditStore
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


class FakeRiskManager:
    state = "TEST_RISK_STATE"

    def validate(self, broker, decision, context=None):
        return True, ""


class FakeAdapter:
    def __init__(self, result):
        self.result = result

    def execute(self, intent, decision):
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
        client_order_id="client-sqlite-1",
    )
    return ctx


def test_pipeline_persists_execution_to_configured_sqlite_store(tmp_path):
    db_path = tmp_path / "execution_audit.db"
    broker = FakeBroker()
    ctx = build_context()
    result = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        intent=ctx.execution_intent,
        broker_order_id="paper-1",
        filled_quantity=75,
        average_fill_price=100,
    )
    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=FakeRiskManager(),
        execution_adapter=FakeAdapter(result),
        audit_db_path=db_path,
    )

    pipeline.execute(ctx)
    pipeline.audit_store.close()

    with SQLiteExecutionAuditStore(db_path) as reopened:
        persisted = reopened.get("client-sqlite-1")
        assert persisted is not None
        assert persisted.status == "EXECUTED"
        assert persisted.broker_order_id == "paper-1"
        assert persisted.filled_quantity == 75
