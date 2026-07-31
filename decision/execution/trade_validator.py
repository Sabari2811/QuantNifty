from decision.validation_result import ValidationResult


class TradeValidator:
    """
    Final validation before execution.

    Produces a ValidationResult instead of
    a simple True / False.
    """

    def validate(self, decision):

        trade = decision.trade
        contract = trade.contract

        warnings = []

        valid = True

        # ----------------------------------
        # Risk / Reward
        # ----------------------------------

        if trade.risk_reward < 1.5:

            warnings.append("Risk/Reward below 1.5")

            # Don't reject immediately.
            # We'll reduce confidence instead.
            valid = True

        # ----------------------------------
        # Premium
        # ----------------------------------

        if trade.entry < 20:

            valid = False

            warnings.append("Premium too low")

        # ----------------------------------
        # Open Interest
        # ----------------------------------

        if contract.oi < 50000:

            valid = False

            warnings.append("Low Open Interest")

        # ----------------------------------
        # Volume
        # ----------------------------------

        if contract.volume < 20000:

            valid = False

            warnings.append("Low Volume")

        # ----------------------------------
        # Grade
        # ----------------------------------

        score = decision.score.get("final", 0)

        if score >= 120:

            grade = "A+"

            confidence = 100

            risk_multiplier = 1.00

        elif score >= 100:

            grade = "A"

            confidence = 90

            risk_multiplier = 0.75

        elif score >= 80:

            grade = "B"

            confidence = 80

            risk_multiplier = 0.50

        elif score >= 60:

            grade = "C"

            confidence = 70

            risk_multiplier = 0.25

        elif score >= 40:

            grade = "D"

            confidence = 50

            risk_multiplier = 0.00

            valid = False

        else:

            grade = "F"

            confidence = 25

            risk_multiplier = 0.00

            valid = False

        return ValidationResult(

            valid=valid,

            grade=grade,

            confidence=confidence,

            risk_multiplier=risk_multiplier,

            warnings=warnings

        )