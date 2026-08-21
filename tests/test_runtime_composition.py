from __future__ import annotations

from runtime.runtime_manager import RuntimeManager


def test_runtime_composition_uses_single_execution_dependency_graph():
    runtime = RuntimeManager()

    composition = runtime.composition
    engine = runtime.engine

    # ------------------------------------------------------
    # CompositionRoot owns the execution dependencies
    # ------------------------------------------------------

    assert composition.paper_broker is not None
    assert composition.risk_manager is not None
    assert composition.intelligence_gate is not None
    assert composition.trade_pipeline is not None

    # ------------------------------------------------------
    # LiveEngine must receive the CompositionRoot instances
    # ------------------------------------------------------

    assert (
        engine.paper_broker
        is composition.paper_broker
    )

    assert (
        engine.risk_manager
        is composition.risk_manager
    )

    assert (
        engine.trade_pipeline
        is composition.trade_pipeline
    )

    # ------------------------------------------------------
    # TradeExecutionPipeline must use the same dependencies
    # ------------------------------------------------------

    assert (
        engine.trade_pipeline.paper_broker
        is composition.paper_broker
    )

    assert (
        engine.trade_pipeline.risk_manager
        is composition.risk_manager
    )

    assert (
        engine.trade_pipeline.intelligence_gate
        is composition.intelligence_gate
    )