from decision.execution.delta_risk import DeltaRiskModel


class PremiumEngine:
    """Build premium entry and delta-aware intraday targets."""

    def __init__(self, movement_model: DeltaRiskModel | None = None):
        self.movement_model = movement_model or DeltaRiskModel()

    def build(self, decision, contract):
        """Populate premium entry and targets using |delta| * underlying move."""
        if contract is None:
            return decision

        trade = decision.trade
        premium = float(getattr(contract, "ltp", 0) or 0)
        delta = float(getattr(contract, "delta", 0) or 0)

        if premium <= 0 or abs(delta) <= 0:
            trade.entry = 0
            trade.target1 = 0
            trade.target2 = 0
            trade.stop_loss = 0
            trade.risk_reward = 0
            return decision

        trade.entry = round(premium, 2)
        _, target1, target2 = self.movement_model.levels(trade.entry, delta)
        trade.target1 = target1
        trade.target2 = target2
        return decision
