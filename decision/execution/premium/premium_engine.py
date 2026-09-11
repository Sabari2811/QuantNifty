from config.trading_config import TradingConfig
from decision.execution.delta_risk import DeltaRiskModel


class PremiumEngine:
    """Build NIFTY option premium entry and delta-aware targets."""

    def __init__(self, movement_model: DeltaRiskModel | None = None):
        self.movement_model = movement_model or DeltaRiskModel()

    def build(self, decision, contract):
        if contract is None:
            return decision
        trade = decision.trade
        premium = float(getattr(contract, "ltp", 0) or 0)
        trade.entry = round(premium, 2) if premium > 0 else 0
        if trade.entry <= 0:
            trade.target1 = 0
            trade.target2 = 0
            trade.stop_loss = 0
            trade.risk_reward = 0
            return decision
        try:
            delta = float(getattr(contract, "delta", 0) or 0)
        except (TypeError, ValueError):
            delta = 0.0
        if abs(delta) <= 0:
            # Historical fixtures without Greeks retain the legacy premium
            # multipliers. Live preparation validates delta before this point.
            trade.target1 = round(trade.entry * TradingConfig.TARGET1_MULTIPLIER, 2)
            trade.target2 = round(trade.entry * TradingConfig.TARGET2_MULTIPLIER, 2)
            return decision
        _, target1, target2 = self.movement_model.levels(trade.entry, delta)
        trade.target1 = target1
        trade.target2 = target2
        return decision
