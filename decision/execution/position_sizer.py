import math


class PositionSizer:
    """
    Calculates the number of lots to trade
    based on account risk.
    """

    def size(

        self,

        decision,

        capital,

        risk_percent,

        lot_size

    ):

        trade = decision.trade

        # ----------------------------------------
        # Total Risk Allowed
        # ----------------------------------------

        risk_amount = capital * risk_percent / 100

        # ----------------------------------------
        # Premium Risk
        # ----------------------------------------

        risk_per_unit = (

            trade.entry -

            trade.stop_loss

        )

        if risk_per_unit <= 0:

            return {

                "lots": 0,

                "capital": capital,

                "risk_amount": risk_amount,

                "risk_per_lot": 0

            }

        # ----------------------------------------
        # Risk Per Lot
        # ----------------------------------------

        risk_per_lot = risk_per_unit * lot_size

        lots = math.floor(

            risk_amount /

            risk_per_lot

        )

        lots = max(

            lots,

            1

        )

        return {

            "lots": lots,

            "capital": capital,

            "risk_amount": round(risk_amount, 2),

            "risk_per_lot": round(risk_per_lot, 2)

        }