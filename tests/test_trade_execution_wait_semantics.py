from types import SimpleNamespace
from unittest.mock import Mock

from execution.trade_execution_pipeline import TradeExecutionPipeline


class _Broker:
    def __init__(self):
        self.portfolio_engine = SimpleNamespace(portfolio=object())
        self.position = None
        self.last_trade = None
        self.journal = SimpleNamespace(summary=lambda: {})
        self.execute = Mock()


class _Risk:
    state = SimpleNamespace()

    def validate(self, *args, **kwargs):
        raise AssertionError("WAIT must not reach the risk execution gate")


def test_wait_decision_is_not_submitted_or_rejected():
    broker = _Broker()
    pipeline = TradeExecutionPipeline(paper_broker=broker, risk_manager=_Risk())
    ctx = SimpleNamespace(
        decision=SimpleNamespace(trade=SimpleNamespace()),
        execution_intent=None,
        intelligence=None,
        decision_intelligence_consistency=None,
    )

    pipeline.execute(ctx)

    assert ctx.trade_status == "NOT_REQUESTED"
    assert ctx.trade_block_reason == ""
    assert ctx.execution_result is None
    assert ctx.execution_lifecycle == ""
    broker.execute.assert_not_called()
