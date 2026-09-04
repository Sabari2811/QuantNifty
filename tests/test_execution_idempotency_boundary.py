from __future__ import annotations

from datetime import datetime

from core.runtime_context import RuntimeContext
from execution.execution_contract import (
    ExecutionAction,
    ExecutionResult,
    ExecutionStatus,
    OrderIntent,
)
from execution.idempotency import IdempotencyStatus, OrderIdempotencyGuard
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
        self.execute_called = 0

    def execute(self, decision):
        self.execute_called += 1
        self.position = "TEST_POSITION"
        self.last_trade = decision.trade
        return self.position


class AllowRiskManager:
    state = "TEST_RISK_STATE"

    def __init__(self):
        self.calls = 0

    def validate(self, broker, decision, context=None):
        self.calls += 1
        return True, ""


def build_context(client_order_id="client-1"):
    ctx = RuntimeContext()
    ctx.decision = type(
        "Decision",
        (),
        {
            "trade": type(
                "Trade",
                (),
                {
                    "symbol": "NIFTY",
                    "option_type": "CE",
                    "strike": 24000,
                    "entry": 100,
                    "execution": type(
                        "Execution",
                        (),
                        {
                            "lot_size": 75,
                            "lots": 1,
                        },
                    )(),
                },
            )(),
            "valid": True,
            "strategy_name": "TEST",
        },
    )()
    ctx.execution_intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        strategy_name="TEST",
        client_order_id=client_order_id,
        created_at=datetime.now(),
    )
    return ctx


def test_pipeline_blocks_duplicate_client_order_id_before_broker_execution():
    broker = FakeBroker()
    risk = AllowRiskManager()
    guard = OrderIdempotencyGuard()
    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk,
        idempotency_guard=guard,
    )

    first = build_context("client-1")
    pipeline.execute(first)
    assert first.trade_status == "EXECUTED"
    assert broker.execute_called == 1

    second = build_context("client-1")
    pipeline.execute(second)

    assert second.trade_status == "BLOCKED"
    assert second.trade_block_reason == "Client order already submitted."
    assert broker.execute_called == 1


def test_pipeline_allows_distinct_client_order_id():
    broker = FakeBroker()
    risk = AllowRiskManager()
    guard = OrderIdempotencyGuard()
    pipeline = TradeExecutionPipeline(
        paper_broker=broker,
        risk_manager=risk,
        idempotency_guard=guard,
    )

    first = build_context("client-1")
    second = build_context("client-2")

    pipeline.execute(first)
    pipeline.execute(second)

    assert first.trade_status == "EXECUTED"
    assert second.trade_status == "EXECUTED"
    assert broker.execute_called == 2


def test_execution_result_preserves_duplicate_block_as_non_execution():
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=24000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=100,
        client_order_id="client-1",
    )
    result = ExecutionResult(
        status=ExecutionStatus.REJECTED,
        intent=intent,
        reason="Client order already submitted.",
    )

    assert result.successful is False
    assert result.terminal is True
    assert result.reason == "Client order already submitted."
