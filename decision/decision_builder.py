from decision.constants import Signal
from decision.models import Decision
from decision.rules import DecisionRules
from decision.validation_result import ValidationResult


class DecisionBuilder:
    """
    Builds the final Decision object.

    Responsibilities
    ----------------
    • Populate market information
    • Populate score breakdown
    • Calculate trade confidence
    • Assign trading signal
    • Initialize validation

    Does NOT perform:
        - Analytics
        - Strategy Selection
        - Execution Planning
        - Order Validation
    """

    def build(
        self,
        market,
        score,
        breakdown,
        reasons,
    ):

        decision = Decision()

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