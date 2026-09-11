from core.runtime_config import RuntimeConfig

from analytics.scoring.score_engine import ScoreEngine
from decision.constants import Signal
from decision.decision_builder import DecisionBuilder
from decision.execution.execution_engine import ExecutionEngine
from decision.market_analyzer import MarketAnalyzer
from decision.nifty_policy import NiftyPolicy
from decision.scoring.directional_score_adapter import DirectionalScoreAdapter
from decision.scoring_engine import ScoringEngine
from decision.strategy_selector import StrategySelector


class DecisionEngine:
    """NIFTY-specific market decision engine.

    The engine decides only the direction of the NIFTY underlying. Option
    contract selection and premium risk are downstream execution concerns.
    """

    VALID_DIRECTIONS = {
        Signal.BUY_CALL.value,
        Signal.BUY_PUT.value,
        Signal.WAIT.value,
    }

    def __init__(self):
        self.policy = NiftyPolicy()
        self.analyzer = MarketAnalyzer()
        self.scoring = ScoreEngine()
        self.directional_adapter = DirectionalScoreAdapter()
        self.legacy_scoring = ScoringEngine()
        self.selector = StrategySelector()
        self.builder = DecisionBuilder()
        self.execution = ExecutionEngine()

    def _validate_nifty_snapshot(self, snapshot):
        market_context = getattr(snapshot, "market_context", None)
        symbol = getattr(market_context, "symbol", "") if market_context is not None else ""
        ok, reason = self.policy.validate_symbol(symbol or self.policy.symbol)
        if not ok:
            raise ValueError(reason)

    def _extract_direction(self, snapshot):
        signal_payload = snapshot.get("signal", None)
        if isinstance(signal_payload, dict):
            direction = signal_payload.get("signal")
        elif isinstance(signal_payload, str):
            direction = signal_payload
        else:
            direction = None
        return direction if direction in self.VALID_DIRECTIONS else None

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
        adapted = self.directional_adapter.adapt(direction=direction, quality_score=quality_score)
        return score_result, adapted["signed_score"], direction

    def _build_legacy_score(self, market):
        score_result = self.legacy_scoring.score(market)
        return score_result["score"], score_result["reasons"], score_result["breakdown"]

    def build(self, snapshot, config: RuntimeConfig | None = None):
        if config is None:
            config = RuntimeConfig()

        self._validate_nifty_snapshot(snapshot)
        market = self.analyzer.analyze(snapshot)
        direction = self._extract_direction(snapshot)

        if direction is not None:
            score_result, score, direction = self._calculate_advanced_score(snapshot, direction)
            institutional = score_result.get("institutional", {})
            reasons = list(institutional.get("reasons", []))
            breakdown = {}
            for component_name in (
                "dealer_score", "liquidity_score", "gamma_score",
                "structure_score", "volatility_score",
            ):
                component = score_result.get(component_name, {})
                breakdown[component_name] = component.get("score", 0)
                reasons.extend(component.get("reasons", []))
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
        breakdown["underlying"] = self.policy.symbol
        breakdown["max_daily_underlying_move"] = self.policy.max_daily_move
        breakdown["max_trade_underlying_move"] = self.policy.max_trade_move
        breakdown["max_trades_per_day"] = self.policy.max_trades_per_day

        decision = self.builder.build(
            market=market,
            score=score,
            breakdown=breakdown,
            reasons=reasons,
            direction=direction,
        )
        decision.strategy_name = strategy_name
        decision.trade.symbol = self.policy.symbol
        decision.authoritative_signal = decision.signal.name
        return self.execution.prepare(decision, snapshot, config)
