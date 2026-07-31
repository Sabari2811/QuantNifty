from datetime import datetime

from models.trade import Trade


class TradeBuilder:
    """
    Builds a standardized Trade object
    from QuantNifty analytics.
    """

    def __init__(self):
        pass

    def build(

        self,

        symbol,

        decision,

        smart_strike,

        trade_plan,

        institutional_score

    ):

        action = decision.get(
            "decision",
            "WAIT"
        )

        if action == "WAIT":

            return None

        return Trade(

            timestamp=datetime.now(),

            symbol=symbol,

            action=action,

            option_type=smart_strike.get(
                "option_type",
                ""
            ),

            strike=float(
                smart_strike.get(
                    "strike",
                    0
                )
            ),

            entry=float(
                trade_plan.get(
                    "entry",
                    0
                )
            ),

            stop_loss=float(
                trade_plan.get(
                    "stop_loss",
                    0
                )
            ),

            target1=float(
                trade_plan.get(
                    "target1",
                    0
                )
            ),

            target2=float(
                trade_plan.get(
                    "target2",
                    0
                )
            ),

            confidence=int(
                decision.get(
                    "confidence",
                    0
                )
            ),

            institutional_score=int(
                institutional_score
                .get("institutional", {})
                .get("score", 0)
            ),

            reasons=decision.get(
                "reasons",
                []
            )
        )