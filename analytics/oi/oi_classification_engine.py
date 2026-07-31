import pandas as pd


class OIClassificationEngine:
    """
    Classifies OI activity using
    OI Change + Premium Change.

    Call Side:
        Long Build-up
        Short Build-up
        Short Covering
        Long Unwinding

    Put Side:
        Same logic.
    """

    def __init__(self):
        pass

    def _classify(self, oi_change, price_change):

        if oi_change > 0 and price_change > 0:
            return "LONG_BUILDUP"

        elif oi_change > 0 and price_change < 0:
            return "SHORT_BUILDUP"

        elif oi_change < 0 and price_change > 0:
            return "SHORT_COVERING"

        elif oi_change < 0 and price_change < 0:
            return "LONG_UNWINDING"

        return "NEUTRAL"

    def calculate(self, market_state):

        df = market_state.copy()

        df["CE_CLASSIFICATION"] = df.apply(

            lambda row: self._classify(

                row["CE_OI_CHANGE"],

                row["CE_LTP_CHANGE"]

            ),

            axis=1

        )

        df["PE_CLASSIFICATION"] = df.apply(

            lambda row: self._classify(

                row["PE_OI_CHANGE"],

                row["PE_LTP_CHANGE"]

            ),

            axis=1

        )

        return df