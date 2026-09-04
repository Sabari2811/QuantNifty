from __future__ import annotations

from types import SimpleNamespace

from engine.live_engine import LiveEngine
from execution.trade_execution_pipeline import TradeExecutionPipeline
from execution.live_execution_runtime_guard import LiveExecutionRuntimeGuard


def test_live_engine_default_execution_pipeline_remains_paper():
    engine = object.__new__(LiveEngine)
    engine.paper_broker = SimpleNamespace()
    engine.risk_manager = SimpleNamespace()
    pipeline = TradeExecutionPipeline(engine.paper_broker, engine.risk_manager)
    engine.trade_pipeline = pipeline

    assert isinstance(engine.trade_pipeline, TradeExecutionPipeline)
    assert not isinstance(engine.trade_pipeline.execution_adapter, LiveExecutionRuntimeGuard)


def test_live_engine_does_not_enable_live_guard_implicitly():
    engine = object.__new__(LiveEngine)
    engine.trade_pipeline = None
    engine.paper_broker = SimpleNamespace()
    engine.risk_manager = SimpleNamespace()

    pipeline = TradeExecutionPipeline(engine.paper_broker, engine.risk_manager)
    engine.trade_pipeline = pipeline

    assert engine.trade_pipeline.execution_adapter.__class__.__name__ == "PaperExecutionAdapter"
