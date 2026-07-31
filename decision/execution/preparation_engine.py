from decision.execution.strike_selector import SmartStrikeSelector
from decision.execution.option_selector import OptionSelector
from decision.execution.premium.premium_engine import PremiumEngine
from decision.execution.risk_engine import RiskEngine
from decision.constants import Signal, OptionType


class PreparationEngine:
    """
    Responsible for preparing the trade
    before execution.

    Responsibilities:
    - Strike selection
    - Option type selection
    - Option contract selection
    - Premium calculation
    - Risk calculation
    """

    def __init__(self):

        self.strike_selector = SmartStrikeSelector()
        self.option_selector = OptionSelector()
        self.premium_engine = PremiumEngine()
        self.risk_engine = RiskEngine()

    def prepare(self, decision, snapshot):

        # --------------------------------------------------
        # Strike Selection
        # --------------------------------------------------

        strike = self.strike_selector.select(

            decision,

            snapshot

        )

        decision.trade.strike = strike

        # --------------------------------------------------
        # Option Type Selection
        # --------------------------------------------------

        if decision.signal.name == Signal.BUY_CALL.value:

            decision.trade.option_type = OptionType.CE.value

        elif decision.signal.name == Signal.BUY_PUT.value:

            decision.trade.option_type = OptionType.PE.value

        else:

            return decision

        # --------------------------------------------------
        # Contract Selection
        # --------------------------------------------------

        contract = self.option_selector.select(

            snapshot,

            strike,

            decision.trade.option_type

        )

        if contract is None:

            decision.valid = False

            decision.reasons.append(

                "No option contract found"

            )

            return decision

        decision.trade.contract = contract

        # --------------------------------------------------
        # Premium Levels
        # --------------------------------------------------

        decision = self.premium_engine.build(

            decision,

            contract

        )

        # --------------------------------------------------
        # Risk Levels
        # --------------------------------------------------

        decision = self.risk_engine.build(

            decision,

            contract

        )

        return decision