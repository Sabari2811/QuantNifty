from __future__ import annotations

from types import SimpleNamespace

from core.runtime_context import RuntimeContext
from engine.live_engine import LiveEngine


class FakeAnalyticsPipeline:
    def __init__(self):
        self.called = False

    def run(
        self,
        greeks_engine,
        greeks_df,
        spot_price,
        candles,
    ):
        self.called = True

        return {
            "greeks": greeks_df,
            "test_metric": 123,
        }


class FakeMarketSnapshot:
    def save(
        self,
        greeks_df,
        spot,
        analytics,
    ):
        return SimpleNamespace(
            greeks_df=greeks_df,
            spot=spot,
            analytics=analytics,
            regime=None,
        )


class FakeMarketRegime:
    def __init__(self):
        self.called = False

    def analyze(self, snapshot):
        self.called = True

        return "TEST_REGIME"


class FakeDecisionEngine:
    def __init__(self):
        self.called = False

    def build(self, snapshot):
        self.called = True

        return SimpleNamespace(
            signal="BUY",
            confidence=80.0,
        )


class FakeExplanationEngine:
    def __init__(self):
        self.called = False

    def build(
        self,
        decision,
        regime,
        snapshot,
    ):
        self.called = True

        return SimpleNamespace(
            explanation="TEST EXPLANATION"
        )


class FakeIntelligenceResult:
    pass


class FakeIntelligenceService:
    def __init__(self):
        self.called = False
        self.received_context = None

        self.result = FakeIntelligenceResult()

    def analyze(self, runtime_context):

        self.called = True

        self.received_context = runtime_context

        return self.result


class FakeTradePipeline:
    def __init__(self):
        self.called = False
        self.received_context = None

    def execute(self, ctx):

        self.called = True

        self.received_context = ctx


class FakeGreeksEngine:
    def __init__(self):
        self.greeks = object()


def build_test_engine():

    engine = LiveEngine.__new__(
        LiveEngine
    )

    engine.ctx = RuntimeContext()

    engine.ctx.spot = 25000.0

    engine.ctx.greeks_df = object()

    engine.ctx.candles = object()

    engine.pipeline = FakeAnalyticsPipeline()

    engine.greeks = FakeGreeksEngine()

    engine.market_regime = FakeMarketRegime()

    engine.decision_engine = FakeDecisionEngine()

    engine.explanation_engine = FakeExplanationEngine()

    engine.intelligence_service = (
        FakeIntelligenceService()
    )

    engine.trade_pipeline = (
        FakeTradePipeline()
    )

    return engine


def test_live_engine_passes_context_to_intelligence_service(
    monkeypatch,
):
    """
    C6.4 integration test.

    Verifies that LiveEngine._run_analytics():

        1. Runs analytics
        2. Builds snapshot
        3. Builds regime
        4. Builds decision
        5. Builds explanation
        6. Invokes IntelligenceService
        7. Stores IntelligenceResult on ctx.intelligence
        8. Continues to trade execution
    """

    monkeypatch.setattr(
        "engine.live_engine.MarketSnapshot",
        FakeMarketSnapshot,
    )

    engine = build_test_engine()

    intelligence_service = (
        engine.intelligence_service
    )

    trade_pipeline = (
        engine.trade_pipeline
    )

    engine._run_analytics()

    #
    # Analytics completed
    #

    assert engine.pipeline.called is True

    assert engine.ctx.analytics is not None

    #
    # Snapshot completed
    #

    assert engine.ctx.snapshot is not None

    #
    # Regime completed
    #

    assert engine.market_regime.called is True

    assert engine.ctx.regime == "TEST_REGIME"

    assert (
        engine.ctx.snapshot.regime
        == "TEST_REGIME"
    )

    #
    # Decision completed
    #

    assert engine.decision_engine.called is True

    assert engine.ctx.decision is not None

    #
    # Explanation completed
    #

    assert engine.explanation_engine.called is True

    assert engine.ctx.explanation is not None

    #
    # Intelligence service was invoked
    #

    assert intelligence_service.called is True

    assert (
        intelligence_service.received_context
        is engine.ctx
    )

    #
    # Intelligence result was stored in
    # RuntimeContext.
    #

    assert (
        engine.ctx.intelligence
        is intelligence_service.result
    )

    #
    # Existing trade execution continues
    # after Intelligence.
    #

    assert trade_pipeline.called is True

    assert (
        trade_pipeline.received_context
        is engine.ctx
    )


def test_live_engine_skips_intelligence_when_service_is_not_configured(
    monkeypatch,
):
    """
    Backward-compatibility test.

    LiveEngine must continue to operate when no
    IntelligenceService is injected.
    """

    monkeypatch.setattr(
        "engine.live_engine.MarketSnapshot",
        FakeMarketSnapshot,
    )

    engine = build_test_engine()

    engine.intelligence_service = None

    engine._run_analytics()

    #
    # Intelligence remains unset.
    #

    assert engine.ctx.intelligence is None

    #
    # Existing pipeline still executes.
    #

    assert (
        engine.trade_pipeline.called is True
    )