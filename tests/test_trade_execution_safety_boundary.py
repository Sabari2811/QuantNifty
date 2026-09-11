from __future__ import annotations

from types import SimpleNamespace

from analytics.intelligence.gate_models import IntelligenceGateResult
from core.runtime_context import RuntimeContext
from execution.execution_contract import ExecutionAction, OrderIntent
from execution.trade_execution_pipeline import TradeExecutionPipeline


class FakePortfolioEngine:
    portfolio = "TEST_PORTFOLIO"


class FakeJournal:
    def summary(self):
        return {"trades": 0}


class FakeBroker:
    def __init__(self):
        self.portfolio_engine = FakePortfolioEngine()
        self.position = None
        self.last_trade = None
        self.journal = FakeJournal()
        self.execute_called = False
        self.reject_execution = False

    def execute(self, decision):
        self.execute_called = True
        if self.reject_execution:
            return None
        self.position = "TEST_POSITION"
        self.last_trade = decision.trade
        return self.position


class FakeRiskManager:
    def __init__(self):
        self.validate_called = False
        self.state = "TEST_RISK_STATE"
        self.allow = True

    def validate(self, broker, decision):
        self.validate_called = True
        return (True, "") if self.allow else (False, "Risk blocked trade.")


class FakeIntelligenceGate:
    def __init__(self, result):
        self.result = result
        self.evaluate_called = False

    def evaluate(self, intelligence):
        self.evaluate_called = True
        return self.result


def build_context():
    ctx = RuntimeContext()
    ctx.decision = SimpleNamespace(trade=SimpleNamespace(symbol="NIFTY"))
    ctx.execution_intent = OrderIntent(
        symbol="NIFTY",
        option_type="PE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=50,
        limit_price=100.0,
        client_order_id="TEST-ORDER-1",
    )
    return ctx


def test_intelligence_block_is_a_hard_execution_boundary():
    broker = FakeBroker()
    risk_manager = FakeRiskManager()
    gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="BLOCK",
        reason="Intelligence data is stale.",
        reasons=("Intelligence data is stale.",),
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=gate)
    ctx = build_context()
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert gate.evaluate_called is True
    assert risk_manager.validate_called is False
    assert broker.execute_called is False
    assert ctx.trade_status == "BLOCKED"
    assert ctx.trade_block_reason == "Intelligence data is stale."


def test_risk_block_is_a_hard_execution_boundary_after_intelligence_allow():
    broker = FakeBroker()
    risk_manager = FakeRiskManager()
    risk_manager.allow = False
    gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="ALLOW", reason="Intelligence allowed."
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=gate)
    ctx = build_context()
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert gate.evaluate_called is True
    assert risk_manager.validate_called is True
    assert broker.execute_called is False
    assert ctx.trade_status == "BLOCKED"
    assert ctx.trade_block_reason == "Risk blocked trade."


def test_intelligence_allow_preserves_execution_path():
    broker = FakeBroker()
    risk_manager = FakeRiskManager()
    gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="ALLOW", reason="Intelligence allowed."
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=gate)
    ctx = build_context()
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert gate.evaluate_called is True
    assert risk_manager.validate_called is True
    assert broker.execute_called is True
    assert ctx.trade_status == "EXECUTED"
    assert ctx.position == "TEST_POSITION"


def test_missing_intelligence_preserves_legacy_risk_path():
    broker = FakeBroker()
    risk_manager = FakeRiskManager()
    gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="BLOCK", reason="Gate must not be called."
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=gate)
    ctx = build_context()
    ctx.intelligence = None
    pipeline.execute(ctx)
    assert gate.evaluate_called is False
    assert risk_manager.validate_called is True
    assert broker.execute_called is True
    assert ctx.trade_status == "EXECUTED"


def test_broker_rejection_is_explicit_after_all_pre_trade_gates_pass():
    broker = FakeBroker()
    broker.reject_execution = True
    risk_manager = FakeRiskManager()
    gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="ALLOW", reason="Intelligence allowed."
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=gate)
    ctx = build_context()
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert gate.evaluate_called is True
    assert risk_manager.validate_called is True
    assert broker.execute_called is True
    assert ctx.trade_status == "REJECTED"
    assert ctx.trade_block_reason == "Paper broker rejected execution"
    assert ctx.position is None


def test_intelligence_block_cannot_leave_previous_execution_status():
    broker = FakeBroker()
    risk_manager = FakeRiskManager()
    allow_gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="ALLOW", reason="Intelligence allowed."
    ))
    pipeline = TradeExecutionPipeline(broker, risk_manager, intelligence_gate=allow_gate)
    ctx = build_context()
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert ctx.trade_status == "EXECUTED"
    assert ctx.position == "TEST_POSITION"

    block_gate = FakeIntelligenceGate(IntelligenceGateResult(
        status="BLOCK",
        reason="Intelligence became stale.",
        reasons=("Intelligence became stale.",),
    ))
    pipeline.intelligence_gate = block_gate
    ctx.intelligence = object()
    pipeline.execute(ctx)
    assert block_gate.evaluate_called is True
    assert ctx.trade_status == "BLOCKED"
    assert ctx.trade_block_reason == "Intelligence became stale."
