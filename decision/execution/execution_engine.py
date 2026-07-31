from core.runtime_config import RuntimeConfig

from decision.constants import Signal
from decision.execution.position_sizer import PositionSizer
from decision.execution.preparation_engine import PreparationEngine
from decision.execution.trade_quality_engine import TradeQualityEngine
from decision.execution.trade_validator import TradeValidator


class ExecutionEngine:
    """
    Converts a trading decision
    into a complete execution plan.

    Responsibilities
    ----------------
    1. Prepare trade
    2. Size position
    3. Calculate trade quality
    4. Validate trade
    5. Populate execution plan
    """

    def __init__(self):

        self.preparation = PreparationEngine()

        self.quality = TradeQualityEngine()

        self.validator = TradeValidator()

        self.position_sizer = PositionSizer()

    def prepare(
        self,
        decision,
        snapshot,
        config: RuntimeConfig | None = None,
    ):

        # --------------------------------------------------
        # Runtime Configuration
        # --------------------------------------------------

        if config is None:

            config = RuntimeConfig()

        # --------------------------------------------------
        # Nothing to Execute
        # --------------------------------------------------

        if decision.signal.name == Signal.WAIT.value:

            return decision

        # --------------------------------------------------
        # Prepare Trade
        # --------------------------------------------------

        decision = self.preparation.prepare(

            decision,

            snapshot

        )

        # --------------------------------------------------
        # No Valid Contract Found
        # --------------------------------------------------

        if decision.trade.contract is None:

            decision.valid = False

            decision.signal.name = Signal.WAIT.value

            return decision

        # --------------------------------------------------
        # Contract Information
        # --------------------------------------------------

        contract = decision.trade.contract

        lot_size = getattr(

            contract,

            "lot_size",

            config.default_lot_size

        )

        # --------------------------------------------------
        # Position Sizing
        # --------------------------------------------------

        position = self.position_sizer.size(

            decision,

            capital=config.capital,

            risk_percent=config.risk_percent,

            lot_size=lot_size

        )

        execution = decision.trade.execution

        execution.capital = position["capital"]

        execution.risk_percent = config.risk_percent

        execution.risk_amount = position["risk_amount"]

        execution.lot_size = lot_size

        execution.lots = position["lots"]

        # --------------------------------------------------
        # Premium Levels
        # --------------------------------------------------

        trade = decision.trade

        execution.premium_entry = trade.entry

        execution.premium_stop_loss = trade.stop_loss

        execution.premium_target1 = trade.target1

        execution.premium_target2 = trade.target2

        execution.risk_reward = trade.risk_reward

        # --------------------------------------------------
        # Trade Quality
        # --------------------------------------------------

        execution.trade_quality = self.quality.score(

            decision

        )

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        validation = self.validator.validate(

            decision

        )

        decision.validation = validation

        decision.valid = validation.valid

        decision.reasons.extend(

            validation.warnings

        )

        if not validation.valid:

            decision.signal.name = Signal.WAIT.value

        return decision