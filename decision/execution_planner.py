from decision.models import Decision
from decision.execution.target_selector import TargetSelector
from decision.execution.strike_selector import SmartStrikeSelector


class ExecutionPlanner:
    """
    Builds an executable trade from a Decision.

    Responsible for:

    - Strike Selection
    - Entry
    - Stop Loss
    - Target Selection
    - Risk / Reward
    """

    def __init__(self):

        self.target_selector = TargetSelector()

        self.strike_selector = SmartStrikeSelector()

    def build(self, decision: Decision, snapshot):

        if not decision.valid:

            return decision

        # ----------------------------------------
        # WAIT
        # ----------------------------------------

        if decision.signal.name == "WAIT":

            decision.trade.strike = None
            decision.trade.option_type = ""
            decision.trade.entry = None
            decision.trade.stop_loss = None
            decision.trade.target1 = None
            decision.trade.target2 = None
            decision.trade.risk_reward = None

            return decision

        expected_move = snapshot.expected_move.get(

            "expected_move",

            100

        )

        # ----------------------------------------
        # Smart Strike Selector
        # ----------------------------------------

        if decision.trade.strike in (0, None):

            decision.trade.strike = self.strike_selector.select(

                decision,

                snapshot

            )

            if decision.signal.name == "BUY CALL":

                decision.trade.option_type = "CE"

            elif decision.signal.name == "BUY PUT":

                decision.trade.option_type = "PE"

        # ----------------------------------------
        # Entry
        # ----------------------------------------

        if decision.trade.entry in (0, None):

            decision.trade.entry = snapshot.spot

        # ----------------------------------------
        # Stop Loss
        # ----------------------------------------

        if decision.trade.stop_loss in (0, None):

            if decision.signal.name == "BUY CALL":

                decision.trade.stop_loss = round(

                    snapshot.spot - expected_move * 0.25,

                    2

                )

            elif decision.signal.name == "BUY PUT":

                decision.trade.stop_loss = round(

                    snapshot.spot + expected_move * 0.25,

                    2

                )

        # ----------------------------------------
        # Smart Target Selector
        # ----------------------------------------

        if decision.trade.target1 in (0, None):

            decision.trade.target1 = self.target_selector.select(

                decision,

                snapshot

            )

        # ----------------------------------------
        # Target 2
        # ----------------------------------------

        if decision.trade.target2 in (0, None):

            if decision.signal.name == "BUY CALL":

                decision.trade.target2 = round(

                    decision.trade.target1 +

                    expected_move * 0.50,

                    2

                )

            elif decision.signal.name == "BUY PUT":

                decision.trade.target2 = round(

                    decision.trade.target1 -

                    expected_move * 0.50,

                    2

                )

        # ----------------------------------------
        # Risk / Reward
        # ----------------------------------------

        try:

            risk = abs(

                decision.trade.entry -

                decision.trade.stop_loss

            )

            reward = abs(

                decision.trade.target1 -

                decision.trade.entry

            )

            if risk > 0:

                decision.trade.risk_reward = round(

                    reward / risk,

                    2

                )

            else:

                decision.trade.risk_reward = None

        except Exception:

            decision.trade.risk_reward = None

        return decision