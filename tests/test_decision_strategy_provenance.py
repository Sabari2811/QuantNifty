from __future__ import annotations

from decision.decision_engine import DecisionEngine


# ==========================================================
# Fake / deterministic collaborators
# ==========================================================


class FakeMarketAnalyzer:

    def analyze(self, snapshot):
        return snapshot


class FakeStrategy:
    """
    Deterministic strategy fixture.

    Strategy identity is an explicit contract.
    It must NOT be inferred from the Python class name.
    """

    name = "FAKE"

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

    The fixture contains the canonical fields required by the
    current DecisionEngine, ScoreEngine and DecisionBuilder
    contracts.
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
        # Market summary consumed by DecisionBuilder
        # --------------------------------------------------

        self.institutional = "NEUTRAL"
        self.probability = 0.0

        # --------------------------------------------------
        # Dealer intelligence
        # --------------------------------------------------

        self.dealer = {
            "dealer_gamma": "LONG",
            "market_mode": "TRENDING",
            "gamma_flip": None,
            "total_gex": 0,
            "expected_volatility": "NORMAL",
        }

        self.dealer_flow = {
            "dealer_delta": "LONG",
            "dealer_vanna": "POSITIVE",
            "dealer_charm": "NEGATIVE",
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
            "market_sentiment": "NEUTRAL",
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


def build_engine():

    engine = DecisionEngine()

    engine.analyzer = FakeMarketAnalyzer()
    engine.selector = FakeStrategySelector()
    engine.execution = FakeExecutionEngine()

    return engine


# ==========================================================
# Strategy provenance
# ==========================================================


def test_decision_preserves_selected_strategy_identity():

    engine = build_engine()

    snapshot = FakeSnapshot()

    decision = engine.build(snapshot)

    # Strategy identity comes from the explicit strategy
    # contract, not from the Python class name.
    assert decision.strategy_name == "FAKE"


def test_decision_strategy_identity_is_not_inferred_from_class_name():

    engine = build_engine()

    snapshot = FakeSnapshot()

    decision = engine.build(snapshot)

    assert decision.strategy_name == "FAKE"

    # Explicitly protect the provenance contract:
    # the strategy name is NOT the Python class name.
    assert decision.strategy_name != "FakeStrategy"