from decision.validation_result import ValidationResult


class TradeValidator:
    """
    Final validation before execution.

    Validation uses TRADE QUALITY, not directional signed score.

    Score contract
    --------------
    quality_score:
        Absolute institutional quality, 0-100.

    signed_score:
        Direction-aware score.

        BUY CALL -> positive
        BUY PUT  -> negative
        WAIT     -> zero

    final:
        Final decision score after strategy adjustment.

    The validator must never interpret a negative signed score
    as poor trade quality.
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

            warnings.append(
                "Risk/Reward below 1.5"
            )

            # Don't reject immediately.
            # We'll reduce confidence instead.
            valid = True

        # ----------------------------------
        # Premium
        # ----------------------------------

        if trade.entry < 20:

            valid = False

            warnings.append(
                "Premium too low"
            )

        # ----------------------------------
        # Open Interest
        # ----------------------------------

        if contract.oi < 50000:

            valid = False

            warnings.append(
                "Low Open Interest"
            )

        # ----------------------------------
        # Volume
        # ----------------------------------

        if contract.volume < 20000:

            valid = False

            warnings.append(
                "Low Volume"
            )

        # ----------------------------------
        # Quality
        # ----------------------------------
        #
        # IMPORTANT:
        #
        # New direction-aware decisions contain:
        #
        #   quality_score = 69
        #   signed_score  = -69   # BUY PUT
        #
        # Validation must use quality_score.
        #
        # Legacy decisions may only contain "final",
        # so retain backward compatibility.
        # ----------------------------------

        quality_score = decision.score.get(
            "quality_score"
        )

        if quality_score is None:

            # Legacy compatibility.
            #
            # Existing decisions used final as an
            # unsigned quality score.
            quality_score = decision.score.get(
                "final",
                0
            )

        quality_score = abs(
            float(quality_score)
        )

        # ----------------------------------
        # Grade
        # ----------------------------------

        if quality_score >= 120:

            grade = "A+"

            confidence = 100

            risk_multiplier = 1.00

        elif quality_score >= 100:

            grade = "A"

            confidence = 90

            risk_multiplier = 0.75

        elif quality_score >= 80:

            grade = "B"

            confidence = 80

            risk_multiplier = 0.50

        elif quality_score >= 60:

            grade = "C"

            confidence = 70

            risk_multiplier = 0.25

        elif quality_score >= 40:

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