from __future__ import annotations

from analytics.intelligence.result import DataQuality
from core.runtime_context import RuntimeContext
from runtime.runtime_manager import RuntimeManager


def test_production_runtime_intelligence_execution_graph_is_connected():
    runtime = RuntimeManager()

    composition = runtime.composition
    engine = runtime.engine

    # ------------------------------------------------------
    # Production composition graph
    # ------------------------------------------------------

    assert engine.paper_broker is composition.paper_broker
    assert engine.risk_manager is composition.risk_manager
    assert engine.trade_pipeline is composition.trade_pipeline

    pipeline = composition.trade_pipeline

    assert pipeline.paper_broker is composition.paper_broker
    assert pipeline.risk_manager is composition.risk_manager
    assert pipeline.intelligence_gate is composition.intelligence_gate

    # ------------------------------------------------------
    # Intelligence gate must be the production gate
    # ------------------------------------------------------

    assert (
        type(composition.intelligence_gate).__name__
        == "IntelligenceGate"
    )

    # ------------------------------------------------------
    # Runtime context can carry Intelligence state
    # ------------------------------------------------------

    ctx = RuntimeContext()

    assert hasattr(ctx, "intelligence")

    # The gate should deterministically allow valid
    # Intelligence data.
    #
    # We don't execute a real trade here because that would
    # make the test dependent on market hours, capital,
    # positions, and broker state.
    # ------------------------------------------------------

    intelligence = type(
        "FakeIntelligence",
        (),
        {
            "data_quality": DataQuality(
                score=100.0,
                stale=False,
                incomplete=False,
                invalid=False,
            )
        },
    )()

    result = composition.intelligence_gate.evaluate(
        intelligence
    )

    assert result.allowed is True
    assert result.blocked is False
    assert result.status == "ALLOW"