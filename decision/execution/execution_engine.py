from core.runtime_config import RuntimeConfig

from decision.constants import Signal
from decision.execution.position_sizer import PositionSizer
from decision.execution.preparation_engine import PreparationEngine
from decision.execution.trade_quality_engine import TradeQualityEngine
from decision.execution.trade_validator import TradeValidator
from decision.nifty_policy import NiftyPolicy


class ExecutionEngine:
    """NIFTY-only execution planner and final trade-quality gate."""

    def __init__(self):
        self.policy = NiftyPolicy()
        self.preparation = PreparationEngine()
        self.quality = TradeQualityEngine()
        self.validator = TradeValidator()
        self.position_sizer = PositionSizer()

    def prepare(self, decision, snapshot, config: RuntimeConfig | None = None):
        if config is None:
            config = RuntimeConfig()

        if decision.signal.name == Signal.WAIT.value:
            return decision

        ok, reason = self.policy.validate_symbol(getattr(decision.trade, "symbol", "NIFTY"))
        if not ok:
            decision.valid = False
            decision.reasons.append(reason)
            decision.signal.name = Signal.WAIT.value
            return decision

        decision = self.preparation.prepare(decision, snapshot)
        if decision.trade.contract is None:
            decision.valid = False
            decision.signal.name = Signal.WAIT.value
            return decision

        contract = decision.trade.contract
        delta_ok, delta_reason = self.policy.validate_delta(getattr(contract, "delta", None))
        if not delta_ok:
            decision.valid = False
            decision.reasons.append(delta_reason)
            decision.signal.name = Signal.WAIT.value
            return decision

        lot_size = getattr(contract, "lot_size", config.default_lot_size)
        position = self.position_sizer.size(
            decision,
            capital=config.capital,
            risk_percent=config.risk_percent,
            lot_size=lot_size,
        )

        execution = decision.trade.execution
        execution.capital = position["capital"]
        execution.risk_percent = config.risk_percent
        execution.risk_amount = position["risk_amount"]
        execution.lot_size = lot_size
        execution.lots = position["lots"]
        execution.premium_entry = decision.trade.entry
        execution.premium_stop_loss = decision.trade.stop_loss
        execution.premium_target1 = decision.trade.target1
        execution.premium_target2 = decision.trade.target2
        execution.risk_reward = decision.trade.risk_reward
        execution.trade_quality = self.quality.score(decision)

        validation = self.validator.validate(decision)
        decision.validation = validation
        decision.valid = validation.valid
        decision.reasons.extend(validation.warnings)
        if not validation.valid:
            decision.signal.name = Signal.WAIT.value
        return decision
