from decision.constants import Signal
from decision.models import Decision
from decision.rules import DecisionRules
from decision.validation_result import ValidationResult


class DecisionBuilder:
    """
    Builds the final Decision object.

    Responsibilities
    ----------------
    - Preserve the authoritative market snapshot
    - Populate market information
    - Populate score breakdown
    - Calculate trade confidence
    - Assign trading signal
    - Initialize validation

    Does NOT perform:
        - Analytics
        - Strategy Selection
        - Execution Planning
        - Order Validation

    Direction Contract
    ------------------
    When an authoritative direction is supplied, it is treated
    as the source of truth for the final trading signal.

    The score represents conviction / quality and must not be
    allowed to manufacture or reverse direction.

    During the migration period, direction=None preserves the
    legacy score-derived behavior.
    """

    def build(
        self,
        market,
        score,
        breakdown,
        reasons,
        direction=None,
    ):
        decision = Decision()

        # ======================================================
        # Authoritative Snapshot Provenance
        # ======================================================

        # Preserve the exact snapshot object used by the
        # decision pipeline. Do not copy or reconstruct it.
        decision.snapshot = market

        # ======================================================
        # Market Information
        # ======================================================

        decision.market.dealer = market.dealer
        decision.market.institutional = market.institutional
        decision.market.probability = market.probability

        # ======================================================
        # Score
        # ======================================================

        decision.score = dict(breakdown)

        trade_confidence = max(
            0,
            min(abs(score), 100)
        )

        decision.signal.confidence = trade_confidence

        decision.reasons = list(reasons)

        # ======================================================
        # Trading Signal
        # ======================================================

        if direction is not None:
            if direction not in {
                Signal.BUY_CALL.value,
                Signal.BUY_PUT.value,
                Signal.WAIT.value,
            }:
                raise ValueError(
                    f"Unsupported decision direction: {direction}"
                )

            # Direction is authoritative.
            decision.signal.name = direction

        else:
            # Legacy compatibility path.
            if score >= DecisionRules.BUY_THRESHOLD:
                decision.signal.name = Signal.BUY_CALL.value

            elif score <= DecisionRules.SELL_THRESHOLD:
                decision.signal.name = Signal.BUY_PUT.value

            else:
                decision.signal.name = Signal.WAIT.value

        # ======================================================
        # Validation
        # ======================================================

        decision.validation = ValidationResult(
            valid=False,
            grade="F",
            confidence=trade_confidence,
            risk_multiplier=0.0,
            warnings=[]
        )

        return decision