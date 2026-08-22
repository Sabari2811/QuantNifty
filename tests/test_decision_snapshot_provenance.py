from __future__ import annotations

from decision.decision_engine import DecisionEngine


# ==========================================================
# Fake / deterministic collaborators
# ==========================================================


class FakeMarketAnalyzer:

    def analyze(self, snapshot):
        return snapshot


class FakeStrategy:

    def adjust(self, score, market):
        return score, []


class FakeStrategySelector:

    def select(self, market):
        return FakeStrategy()


class FakeExecutionEngine:

    def prepare(
        self,
        decision,
        snapshot,
        config,
    ):
        decision.execution_snapshot = snapshot
        return decision


# ==========================================================
# Canonical deterministic snapshot fixture
# ==========================================================


class FakeSnapshot(dict):
    """
    Deterministic snapshot fixture.

    Supports both:

        snapshot.get(...)

    and:

        snapshot.<field>
    """

    def __init__(self):

        super().__init__(
            signal={
                "signal": "WAIT",
                "confidence": 0,
                "reasons": [],
            }
        )

        # --------------------------------------------------
        # Dealer intelligence
        # --------------------------------------------------

        self.dealer = {
            "dealer_gamma": "LONG",
            "market_mode": "TRENDING",
            "gamma_flip": None,
            "total_gex": 0,
        }

        self.dealer_flow = {
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
        }

        # --------------------------------------------------
        # Institutional intelligence
        # --------------------------------------------------

        self.institutional = {
            "score": 0,
            "bias": "NEUTRAL",
        }
        # --------------------------------------------------
        # Probability
        # --------------------------------------------------

        self.probability = {
            "probability": 0.50,
        }        

        # --------------------------------------------------
        # Liquidity
        # --------------------------------------------------

        self.liquidity = {
            "support": 24200,
            "resistance": 24350,
            "absorption": {
                "count": 0,
            },
            "order_imbalance": {
                "buy_pressure": False,
                "sell_pressure": False,
            },
        }

        # --------------------------------------------------
        # Market structure
        # --------------------------------------------------

        self.market_structure = {
            "trend": "BULLISH",
            "structure": "UPTREND",
        }

        # --------------------------------------------------
        # PCR
        # --------------------------------------------------

        self.pcr = {
            "pcr": 1.0,
        }

        # --------------------------------------------------
        # Expected move
        # --------------------------------------------------

        self.expected_move = {
            "upper": 24400,
            "lower": 24150,
        }

        # --------------------------------------------------
        # IV skew / smile
        # --------------------------------------------------

        self.iv_skew = {
            "skew": 0.0,
        }

        self.iv_smile = {
            "smile": 0.0,
        }

        # --------------------------------------------------
        # ATR / volatility
        # --------------------------------------------------

        self.atr = {
            "atr": 100,
            "volatility": "NORMAL",
        }

        # --------------------------------------------------
        # Market price
        # --------------------------------------------------

        self.spot = 24270.85


# ==========================================================
# Fixtures
# ==========================================================


def build_snapshot():

    return FakeSnapshot()


def build_engine():

    engine = DecisionEngine()

    engine.analyzer = FakeMarketAnalyzer()
    engine.selector = FakeStrategySelector()
    engine.execution = FakeExecutionEngine()

    return engine


# ==========================================================
# Snapshot provenance
# ==========================================================


def test_decision_pipeline_preserves_authoritative_snapshot_identity():

    engine = build_engine()

    snapshot = build_snapshot()

    decision = engine.build(snapshot)

    # Decision must retain the exact authoritative
    # snapshot supplied to DecisionEngine.build().
    assert decision.snapshot is snapshot

    # Execution preparation must receive the exact
    # same snapshot object.
    assert decision.execution_snapshot is snapshot


def test_decision_builder_receives_same_snapshot_used_for_analysis():

    engine = build_engine()

    observed = {}

    class ObservingAnalyzer:

        def analyze(self, snapshot):

            observed["snapshot"] = snapshot

            return snapshot

    engine.analyzer = ObservingAnalyzer()

    snapshot = build_snapshot()

    decision = engine.build(snapshot)

    # Analyzer receives the authoritative snapshot.
    assert observed["snapshot"] is snapshot

    # Decision preserves that same object.
    assert decision.snapshot is snapshot


def test_execution_boundary_receives_authoritative_snapshot():

    engine = build_engine()

    observed = {}

    class ObservingExecutionEngine:

        def prepare(
            self,
            decision,
            snapshot,
            config,
        ):

            observed["snapshot"] = snapshot

            return decision

    engine.execution = ObservingExecutionEngine()

    snapshot = build_snapshot()

    engine.build(snapshot)

    # Execution boundary receives the exact authoritative
    # snapshot object.
    assert observed["snapshot"] is snapshot