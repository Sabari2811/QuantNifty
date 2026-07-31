from core.runtime_config import RuntimeConfig

from decision.market_analyzer import MarketAnalyzer
from decision.strategy_selector import StrategySelector
from decision.scoring_engine import ScoringEngine
from decision.decision_builder import DecisionBuilder
from decision.execution.execution_engine import ExecutionEngine


class DecisionEngine:
    """
    QuantNifty Decision Engine

    Pipeline

        Market Snapshot
                │
                ▼
        Market Analyzer
                │
                ▼
        Scoring Engine
                │
                ▼
        Strategy Selector
                │
                ▼
        Decision Builder
                │
                ▼
        Execution Engine
    """

    def __init__(self):

        self.analyzer = MarketAnalyzer()

        self.scoring = ScoringEngine()

        self.selector = StrategySelector()

        self.builder = DecisionBuilder()

        self.execution = ExecutionEngine()

    def build(
        self,
        snapshot,
        config: RuntimeConfig | None = None,
    ):

        # --------------------------------------------
        # Runtime Configuration
        # --------------------------------------------

        if config is None:

            config = RuntimeConfig()

        # --------------------------------------------
        # Market Analysis
        # --------------------------------------------

        market = self.analyzer.analyze(

            snapshot

        )

        # --------------------------------------------
        # Base Scoring
        # --------------------------------------------

        score_result = self.scoring.score(

            market

        )

        score = score_result["score"]

        reasons = score_result["reasons"]

        breakdown = score_result["breakdown"]

        # --------------------------------------------
        # Strategy Adjustment
        # --------------------------------------------

        strategy = self.selector.select(

            market

        )

        score, strategy_reasons = strategy.adjust(

            score,

            market

        )

        reasons.extend(

            strategy_reasons

        )

        breakdown["strategy"] = (

            score - breakdown["total"]

        )

        breakdown["final"] = score

        # --------------------------------------------
        # Decision
        # --------------------------------------------

        decision = self.builder.build(

            market=market,

            score=score,

            breakdown=breakdown,

            reasons=reasons

        )

        # --------------------------------------------
        # Execution Plan
        # --------------------------------------------

        decision = self.execution.prepare(

            decision,

            snapshot,

            config

        )

        return decision