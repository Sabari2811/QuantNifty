class RiskEngine:
    """
    QuantNifty Risk Engine
    """

    # ======================================================
    # Standard API
    # ======================================================

    def generate(

        self,

        trade_plan,

        capital=500000,

        risk_percent=1

    ):

        risk_amount = capital * risk_percent / 100

        signal = trade_plan["signal"]

        if signal == "WAIT":

            return {

                "capital": capital,

                "risk_percent": risk_percent,

                "risk_amount": risk_amount,

                "points_risk": 0,

                "points_reward": 0,

                "risk_reward": "-",

                "suggested_lots": 0

            }

        entry = trade_plan["entry"]

        stop_loss = trade_plan["stop_loss"]

        target = trade_plan["target2"]

        points_risk = abs(entry - stop_loss)

        points_reward = abs(target - entry)

        rr = (

            round(points_reward / points_risk, 2)

            if points_risk

            else 0

        )

        lot_size = 65

        loss_per_lot = points_risk * lot_size

        lots = (

            max(

                1,

                int(risk_amount / loss_per_lot)

            )

            if loss_per_lot

            else 0

        )

        return {

            "capital": capital,

            "risk_percent": risk_percent,

            "risk_amount": risk_amount,

            "points_risk": round(points_risk, 2),

            "points_reward": round(points_reward, 2),

            "risk_reward": f"1 : {rr}",

            "suggested_lots": lots

        }

    # ======================================================
    # Backward Compatibility
    # ======================================================

    def calculate(

        self,

        trade_plan,

        capital=500000,

        risk_percent=1

    ):

        return self.generate(

            trade_plan,

            capital,

            risk_percent

        )