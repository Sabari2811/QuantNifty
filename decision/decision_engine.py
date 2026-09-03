from core.runtime_config import RuntimeConfig

from decision.market_analyzer import MarketAnalyzer
from decision.strategy_selector import StrategySelector

# Legacy scorer retained temporarily for backward compatibility
# with older MarketSnapshot fixtures that do not contain signal data.
from decision.scoring_engine import ScoringEngine

from decision.scoring.directional_score_adapter import (
    DirectionalScoreAdapter
)

from analytics.scoring.score_engine import ScoreEngine

from decision.decision_builder import DecisionBuilder
from decision.execution.execution_engine import ExecutionEngine


class DecisionEngine:
    """
    QuantNifty Decision Engine

    R2-003 Direction-Aware Architecture
    """

    VALID_DIRECTIONS = {
        "BUY CALL",
        "BUY PUT",
        "WAIT",
    }

    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.scoring = ScoreEngine()
        self.directional_adapter = DirectionalScoreAdapter()
        self.legacy_scoring = ScoringEngine()
        self.selector = StrategySelector()
        self.builder = DecisionBuilder()
        self.execution = ExecutionEngine()

    def _extract_direction(self, snapshot):
        # MarketSnapshot.get() resolves declared fields from the typed
        # canonical MarketContext first. Using the mapping-style interface
        # here also preserves compatibility with legacy/fake snapshots that
        # implement get() without exposing every shortcut as an attribute.
        signal_payload = snapshot.get("signal", None)
        if isinstance(signal_payload, dict):
            direction = signal_payload.get("signal")
        elif isinstance(signal_payload, str):
            direction = signal_payload
        else:
            direction = None
        if direction in self.VALID_DIRECTIONS:
            return direction
        return None

    def _calculate_advanced_score(self, snapshot, direction):
        signal_payload = snapshot.get("signal", {"signal": direction})
        if not isinstance(signal_payload, dict):
            signal_payload = {"signal": direction}
        score_result = self.scoring.calculate(
            dealer=snapshot.dealer,
            dealer_flow=snapshot.dealer_flow,
            liquidity=snapshot.liquidity,
            market_structure=snapshot.market_structure,
            pcr=snapshot.pcr,
            expected_move=snapshot.expected_move,
            iv_skew=snapshot.iv_skew,
            iv_smile=snapshot.iv_smile,
            atr=snapshot.atr,
            spot=snapshot.spot,
            signal=signal_payload,
        )
        institutional = score_result.get("institutional", {})
        quality_score = institutional.get("score", 0)
        adapted = self.directional_adapter.adapt(
            direction=direction,
            quality_score=quality_score,
        )
        return score_result, adapted["signed_score"], direction

    def _build_legacy_score(self, market):
        score_result = self.legacy_scoring.score(market)
        return (
            score_result["score"],
            score_result["reasons"],
            score_result["breakdown"],
        )

    def build(self, snapshot, config: RuntimeConfig | None = None):
        if config is None:
            config = RuntimeConfig()

        market = self.analyzer.analyze(snapshot)
        direction = self._extract_direction(snapshot)

        if direction is not None:
            score_result, score, direction = self._calculate_advanced_score(
                snapshot=snapshot,
                direction=direction,
            )
            institutional = score_result.get("institutional", {})
            reasons = list(institutional.get("reasons", []))

            for component_name in (
                "dealer_score",
                "liquidity_score",
                "gamma_score",
                "structure_score",
                "volatility_score",
            ):
                component = score_result.get(component_name, {})
                component_reasons = component.get("reasons", [])
                if component_reasons:
                    reasons.extend(component_reasons)

            breakdown = {}
            for component_name in (
                "dealer_score",
                "liquidity_score",
                "gamma_score",
                "structure_score",
                "volatility_score",
            ):
                component = score_result.get(component_name, {})
                breakdown[component_name] = component.get("score", 0)

            breakdown["institutional"] = institutional.get("score", 0)
            breakdown["direction"] = direction
            breakdown["quality_score"] = institutional.get("score", 0)
            breakdown["signed_score"] = score
        else:
            score, reasons, breakdown = self._build_legacy_score(market)

        strategy = self.selector.select(market)
        strategy_name = strategy.name
        score_before_strategy = score
        score, strategy_reasons = strategy.adjust(score, market)
        reasons.extend(strategy_reasons)
        breakdown["strategy"] = score - score_before_strategy
        breakdown["final"] = score

        decision = self.builder.build(
            market=market,
            score=score,
            breakdown=breakdown,
            reasons=reasons,
            direction=direction,
        )
        decision.strategy_name = strategy_name

        # Capture the authoritative Decision signal before execution planning.
        # ExecutionEngine may later change signal.name to WAIT when validation
        # or contract preparation fails; that is an execution state, not a
        # replacement for the market Decision used by reconciliation.
        decision.authoritative_signal = decision.signal.name

        decision = self.execution.prepare(decision, snapshot, config)
        return decision
