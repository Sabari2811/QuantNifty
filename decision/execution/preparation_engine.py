from decision.constants import Signal, OptionType
from decision.execution.strike_selector import SmartStrikeSelector
from decision.execution.option_selector import OptionSelector
from decision.execution.premium.premium_engine import PremiumEngine
from decision.execution.risk_engine import RiskEngine
from decision.nifty_policy import NiftyPolicy


class PreparationEngine:
    """Prepare the executable NIFTY CE/PE contract and risk levels."""

    def __init__(self):
        self.policy = NiftyPolicy()
        self.strike_selector = SmartStrikeSelector()
        self.option_selector = OptionSelector()
        self.premium_engine = PremiumEngine()
        self.risk_engine = RiskEngine()

    def prepare(self, decision, snapshot):
        decision.trade.symbol = self.policy.symbol

        strike = self.strike_selector.select(decision, snapshot)
        if strike is None:
            decision.valid = False
            decision.reasons.append("NIFTY strike unavailable")
            return decision
        decision.trade.strike = strike

        if decision.signal.name == Signal.BUY_CALL.value:
            decision.trade.option_type = OptionType.CE.value
        elif decision.signal.name == Signal.BUY_PUT.value:
            decision.trade.option_type = OptionType.PE.value
        else:
            return decision

        ok, reason = self.policy.validate_option(decision.trade.option_type)
        if not ok:
            decision.valid = False
            decision.reasons.append(reason)
            return decision

        contract = self.option_selector.select(snapshot, strike, decision.trade.option_type)
        if contract is None:
            decision.valid = False
            decision.reasons.append("No NIFTY option contract found")
            return decision

        delta_ok, delta_reason = self.policy.validate_delta(contract.delta)
        if not delta_ok:
            decision.valid = False
            decision.reasons.append(delta_reason)
            return decision

        decision.trade.contract = contract
        decision = self.premium_engine.build(decision, contract)
        decision = self.risk_engine.build(decision, contract)
        return decision
