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
    ------------------------------------

        Market Snapshot
                │
                ▼
        Market Analyzer
                │
                ├───────────────┐
                │               │
                ▼               ▼
        Signal / Direction   Advanced Score
                │               │
                │               ▼
                │       Institutional Quality
                │               │
                │               ▼
                │      DirectionalScoreAdapter
                │               │
                └───────────────┤
                                ▼
                         Strategy Selector
                                │
                                ▼
                         Decision Builder
                                │
                                ▼
                         Execution Engine

    Direction
        Comes from SignalEngine / snapshot signal.

    Quality
        Comes from analytics.scoring.ScoreEngine.

    The DirectionalScoreAdapter converts:

        BUY CALL + quality → positive score
        BUY PUT  + quality → negative score
        WAIT     + quality → zero score

    Migration behavior
    ------------------
    Older snapshots without a valid signal temporarily use the
    legacy ScoringEngine so existing historical/unit fixtures remain
    compatible.

    The legacy scorer will be removed only after the comparison and
    regression phases are completed.
    """

    VALID_DIRECTIONS = {
        "BUY CALL",
        "BUY PUT",
        "WAIT",
    }

    def __init__(self):

        self.analyzer = MarketAnalyzer()

        # --------------------------------------------------------
        # R2-003 Advanced Scoring
        # --------------------------------------------------------

        self.scoring = ScoreEngine()

        self.directional_adapter = DirectionalScoreAdapter()

        # --------------------------------------------------------
        # Temporary backward compatibility
        # --------------------------------------------------------

        self.legacy_scoring = ScoringEngine()

        # --------------------------------------------------------
        # Existing decision pipeline
        # --------------------------------------------------------

        self.selector = StrategySelector()

        self.builder = DecisionBuilder()

        self.execution = ExecutionEngine()

    def _extract_direction(self, snapshot):
        """
        Extract the authoritative SignalEngine direction.

        Canonical MarketSnapshot stores the signal inside its
        analytics dictionary.

        Expected structure:

            {
                "signal": "BUY CALL",
                "confidence": ...,
                "spot": ...,
                "reasons": [...]
            }

        Returns:
            "BUY CALL"
            "BUY PUT"
            "WAIT"
            None
        """

        signal_payload = snapshot.get("signal", None)

        if isinstance(signal_payload, dict):

            direction = signal_payload.get(
                "signal"
            )

        elif isinstance(signal_payload, str):

            direction = signal_payload

        else:

            direction = None

        if direction in self.VALID_DIRECTIONS:
            return direction

        return None

    def _calculate_advanced_score(
        self,
        snapshot,
        direction,
    ):
        """
        Calculate institutional quality using the advanced
        analytics ScoreEngine.

        Returns:
            score_result
            signed_score
            direction
        """

        signal_payload = snapshot.get(
            "signal",
            {
                "signal": direction
            }
        )

        if not isinstance(signal_payload, dict):
            signal_payload = {
                "signal": direction
            }

        score_result = self.scoring.calculate(
            dealer=snapshot.dealer,
            dealer_flow=snapshot.dealer_flow,
            liquidity=snapshot.liquidity,
            market_structure=snapshot.market_structure,
            pcr=snapshot.pcr,
            expected_move=snapshot.expected_move,
            iv_skew=snapshot.get("iv_skew", {}),
            iv_smile=snapshot.get("iv_smile", {}),
            atr=snapshot.atr,
            spot=snapshot.spot,
            signal=signal_payload,
        )

        institutional = score_result.get(
            "institutional",
            {}
        )

        quality_score = institutional.get(
            "score",
            0
        )

        adapted = self.directional_adapter.adapt(
            direction=direction,
            quality_score=quality_score,
        )

        return (
            score_result,
            adapted["signed_score"],
            direction,
        )

    def _build_legacy_score(
        self,
        market,
    ):
        """
        Temporary compatibility path for old snapshots that do
        not contain the new authoritative signal contract.
        """

        score_result = self.legacy_scoring.score(
            market
        )

        return (
            score_result["score"],
            score_result["reasons"],
            score_result["breakdown"],
        )

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
        # Direction
        # --------------------------------------------

        direction = self._extract_direction(
            snapshot
        )

        # --------------------------------------------
        # Scoring
        # --------------------------------------------

        if direction is not None:

            # ====================================================
            # R2-003 NEW PATH
            # ====================================================

            score_result, score, direction = (
                self._calculate_advanced_score(
                    snapshot=snapshot,
                    direction=direction,
                )
            )

            institutional = score_result.get(
                "institutional",
                {}
            )

            reasons = list(
                institutional.get(
                    "reasons",
                    []
                )
            )

            # Collect component reasons when available.
            for component_name in (
                "dealer_score",
                "liquidity_score",
                "gamma_score",
                "structure_score",
                "volatility_score",
            ):

                component = score_result.get(
                    component_name,
                    {}
                )

                component_reasons = component.get(
                    "reasons",
                    []
                )

                if component_reasons:
                    reasons.extend(
                        component_reasons
                    )

            breakdown = {}

            for component_name in (
                "dealer_score",
                "liquidity_score",
                "gamma_score",
                "structure_score",
                "volatility_score",
            ):

                component = score_result.get(
                    component_name,
                    {}
                )

                breakdown[component_name] = component.get(
                    "score",
                    0
                )

            breakdown["institutional"] = (
                institutional.get(
                    "score",
                    0
                )
            )

            breakdown["direction"] = direction

            breakdown["quality_score"] = (
                institutional.get(
                    "score",
                    0
                )
            )

            breakdown["signed_score"] = score

        else:

            # ====================================================
            # LEGACY COMPATIBILITY PATH
            # ====================================================

            (
                score,
                reasons,
                breakdown,
            ) = self._build_legacy_score(
                market
            )

        # --------------------------------------------
        # Strategy Adjustment
        # --------------------------------------------

        strategy = self.selector.select(
            market
        )

        score_before_strategy = score

        score, strategy_reasons = strategy.adjust(
            score,
            market
        )

        reasons.extend(
            strategy_reasons
        )

        breakdown["strategy"] = (
            score - score_before_strategy
        )

        breakdown["final"] = score

        # --------------------------------------------
        # Decision
        # --------------------------------------------

        decision = self.builder.build(
            market=market,

            score=score,

            breakdown=breakdown,

            reasons=reasons,

            direction=direction,
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