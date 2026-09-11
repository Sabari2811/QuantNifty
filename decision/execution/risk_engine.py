from decision.execution.delta_risk import DeltaRiskModel


class RiskEngine:
    """Calculate premium risk from option delta and bounded NIFTY movement."""

    def __init__(self, movement_model: DeltaRiskModel | None = None):
        self.movement_model = movement_model or DeltaRiskModel()

    def build(self, decision, contract):
        """Populate stop loss and risk/reward for the selected intraday trade."""
        if contract is None:
            return decision

        trade = decision.trade
        premium = float(getattr(contract, "ltp", 0) or 0)
        delta = float(getattr(contract, "delta", 0) or 0)

        if premium <= 0 or abs(delta) <= 0 or trade.entry <= 0:
            trade.stop_loss = 0
            trade.risk_reward = 0
            return decision

        stop_loss, target1, target2 = self.movement_model.levels(trade.entry, delta)
        trade.stop_loss = stop_loss

        # PremiumEngine owns targets. Recalculate only to guarantee that risk
        # and target calculations use the exact same delta/movement model.
        trade.target1 = target1
        trade.target2 = target2

        risk = trade.entry - trade.stop_loss
        reward = trade.target1 - trade.entry
        trade.risk_reward = round(reward / risk, 2) if risk > 0 else 0
        return decision
