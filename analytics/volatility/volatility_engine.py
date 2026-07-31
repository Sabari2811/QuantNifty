"""
============================================================
Volatility Engine
============================================================

Aggregates all volatility analytics into a single object.

This engine DOES NOT perform calculations.

It simply combines:

    • IV Skew
    • IV Smile
    • Expected Move
    • ATR

into one standardized structure for the UI.

============================================================
"""


class VolatilityEngine:

    def __init__(self):
        pass

    # ==========================================================
    # MAIN
    # ==========================================================

    def analyze(
        self,
        iv_skew,
        iv_smile,
        expected_move,
        atr,
        spot,
    ):

        # ------------------------------------------------------
        # Expected Move
        # ------------------------------------------------------

        lower = expected_move.get("lower")
        upper = expected_move.get("upper")

        move_points = None
        move_percent = None

        if (
            isinstance(lower, (int, float))
            and isinstance(upper, (int, float))
        ):

            move_points = round((upper - lower) / 2, 2)

            if spot:

                move_percent = round(
                    (move_points / spot) * 100,
                    2
                )

        # ------------------------------------------------------
        # ATR
        # ------------------------------------------------------

        atr_value = atr.get("atr")

        volatility_level = atr.get(
            "volatility",
            "UNKNOWN"
        )

        # ------------------------------------------------------
        # Market Condition
        # ------------------------------------------------------

        if volatility_level in ["HIGH", "VERY HIGH"]:

            market_condition = "EXPANDING"

        elif volatility_level == "LOW":

            market_condition = "CONTRACTING"

        else:

            market_condition = "NORMAL"

        # ------------------------------------------------------
        # Output
        # ------------------------------------------------------

        return {

            "iv_skew": iv_skew,

            "iv_smile": iv_smile,

            "expected_move": expected_move,

            "atr": atr,

            "spot": spot,

            "expected_move_points": move_points,

            "expected_move_percent": move_percent,

            "atr_value": atr_value,

            "volatility_level": volatility_level,

            "market_condition": market_condition

        }