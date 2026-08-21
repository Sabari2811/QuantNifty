from __future__ import annotations

from types import SimpleNamespace

from analytics.intelligence.gate_models import (
    IntelligenceGateResult,
)

from core.runtime_context import RuntimeContext

from execution.trade_execution_pipeline import (
    TradeExecutionPipeline,
)


# ==========================================================
# Fake collaborators
# ==========================================================


class FakePortfolioEngine:

    portfolio = "TEST_PORTFOLIO"


class FakeJournal:

    def summary(self):

        return {
            "trades": 0,
        }


class FakeBroker:

    def __init__(self):

        self.portfolio_engine = (
            FakePortfolioEngine()
        )

        self.position = None

        self.last_trade = None

        self.journal = FakeJournal()

        self.execute_called = False

    def execute(self, decision):

        self.execute_called = True

        self.position = "TEST_POSITION"

        self.last_trade = decision.trade

        return self.position


class FakeRiskManager:

    def __init__(self):

        self.validate_called = False

        self.state = "TEST_RISK_STATE"

        self.allow = True

    def validate(
        self,
        broker,
        decision,
    ):

        self.validate_called = True

        if self.allow:

            return True, ""

        return (
            False,
            "Risk blocked trade.",
        )


class FakeIntelligenceGate:

    def __init__(
        self,
        result,
    ):

        self.result = result

        self.evaluate_called = False

        self.received = None

    def evaluate(
        self,
        intelligence,
    ):

        self.evaluate_called = True

        self.received = intelligence

        return self.result


# ==========================================================
# Test fixtures
# ==========================================================


def build_decision():

    return SimpleNamespace(

        trade=SimpleNamespace(
            symbol="NIFTY",
        )

    )


def build_intelligence():

    return object()


def build_context():

    ctx = RuntimeContext()

    ctx.decision = build_decision()

    return ctx


# ==========================================================
# C8.2 — Intelligence BLOCK
# ==========================================================


def test_intelligence_block_prevents_risk_manager_and_broker():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="BLOCK",
            reason="Intelligence data is stale.",
            reasons=(
                "Intelligence data is stale.",
            ),
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = build_context()

    ctx.intelligence = build_intelligence()

    pipeline.execute(ctx)

    assert gate.evaluate_called is True

    assert (
        gate.received
        is ctx.intelligence
    )

    assert (
        risk_manager.validate_called
        is False
    )

    assert (
        broker.execute_called
        is False
    )

    assert (
        ctx.trade_status
        == "BLOCKED"
    )

    assert (
        ctx.trade_block_reason
        == "Intelligence data is stale."
    )


# ==========================================================
# C8.2 — Intelligence ALLOW
# ==========================================================


def test_intelligence_allow_continues_to_risk_manager_and_broker():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="ALLOW",
            reason=(
                "Intelligence data quality is acceptable."
            ),
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = build_context()

    ctx.intelligence = build_intelligence()

    pipeline.execute(ctx)

    assert gate.evaluate_called is True

    assert (
        risk_manager.validate_called
        is True
    )

    assert (
        broker.execute_called
        is True
    )

    assert (
        ctx.trade_status
        == "EXECUTED"
    )

    assert (
        ctx.position
        == "TEST_POSITION"
    )

    assert (
        ctx.last_trade
        is ctx.decision.trade
    )


# ==========================================================
# C8.2 — Intelligence unavailable
# ==========================================================


def test_missing_intelligence_preserves_existing_execution_path():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="BLOCK",
            reason="This gate must not be called.",
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = build_context()

    ctx.intelligence = None

    pipeline.execute(ctx)

    assert (
        gate.evaluate_called
        is False
    )

    assert (
        risk_manager.validate_called
        is True
    )

    assert (
        broker.execute_called
        is True
    )

    assert (
        ctx.trade_status
        == "EXECUTED"
    )

    assert (
        ctx.position
        == "TEST_POSITION"
    )


# ==========================================================
# C8.2 — RiskManager remains authoritative
# ==========================================================


def test_intelligence_allow_does_not_bypass_risk_manager():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    risk_manager.allow = False

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="ALLOW",
            reason="Intelligence allowed.",
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = build_context()

    ctx.intelligence = build_intelligence()

    pipeline.execute(ctx)

    assert gate.evaluate_called is True

    assert (
        risk_manager.validate_called
        is True
    )

    assert (
        broker.execute_called
        is False
    )

    assert (
        ctx.trade_status
        == "BLOCKED"
    )

    assert (
        ctx.trade_block_reason
        == "Risk blocked trade."
    )


# ==========================================================
# C8.2 — No decision
# ==========================================================


def test_no_decision_does_not_call_intelligence_gate():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="BLOCK",
            reason="Must not be called.",
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = RuntimeContext()

    ctx.intelligence = build_intelligence()

    pipeline.execute(ctx)

    assert (
        gate.evaluate_called
        is False
    )

    assert (
        risk_manager.validate_called
        is False
    )

    assert (
        broker.execute_called
        is False
    )


# ==========================================================
# C8.2 — No trade
# ==========================================================


def test_decision_without_trade_does_not_call_intelligence_gate():

    broker = FakeBroker()

    risk_manager = FakeRiskManager()

    gate = FakeIntelligenceGate(
        IntelligenceGateResult(
            status="BLOCK",
            reason="Must not be called.",
        )
    )

    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk_manager,
        intelligence_gate=gate,
    )

    ctx = RuntimeContext()

    ctx.decision = SimpleNamespace(
        trade=None,
    )

    ctx.intelligence = build_intelligence()

    pipeline.execute(ctx)

    assert (
        gate.evaluate_called
        is False
    )

    assert (
        risk_manager.validate_called
        is False
    )

    assert (
        broker.execute_called
        is False
    )