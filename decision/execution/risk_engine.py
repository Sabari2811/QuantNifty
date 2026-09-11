from config.trading_config import TradingConfig
from decision.execution.delta_risk import DeltaRiskModel


class RiskEngine:
    """Calculate premium risk from option delta and bounded NIFTY movement."""

    def __init__(self, movement_model: DeltaRiskModel | None = None):
        self.movement_model = movement_model or DeltaRiskModel()

    @staticmethod
    def _risk_percent(iv):
        """Legacy IV-based fallback used only when delta is unavailable."""
        try:
            value = float(iv)
        except (TypeError, ValueError):
            value = TradingConfig.HIGH_IV_THRESHOLD
        if value >= TradingConfig.HIGH_IV_THRESHOLD:
            return TradingConfig.STOPLOSS_HIGH_IV
        if value <= TradingConfig.LOW_IV_THRESHOLD:
            return TradingConfig.STOPLOSS_LOW_IV
        return TradingConfig.STOPLOSS_NORMAL_IV

    def build(self, decision, contract):
        """Populate stop loss and risk/reward for the selected intraday trade."""
        if contract is None:
            return decision

        trade = decision.trade
        premium = float(getattr(contract, "ltp", 0) or 0)
        delta_raw = getattr(contract, "delta", None)
        try:
            delta = float(delta_raw)
        except (TypeError, ValueError):
            delta = 0.0

        # Keep a compatibility path for older replay/unit fixtures that do not
        # contain Greeks. Live NIFTY preparation rejects missing/unusable delta
        # before this engine is called.
        if premium <= 0 or trade.entry <= 0:
            trade.stop_loss = 0
            trade.risk_reward = 0
            return decision

        if abs(delta) <= 0:
            trade.stop_loss = round(
                premium * (1 - self._risk_percent(getattr(contract, "iv", None))),
                2,
            )
            risk = trade.entry - trade.stop_loss
            reward = trade.target1 - trade.entry
            trade.risk_reward = round(reward / risk, 2) if risk > 0 else 0
            return decision

        stop_loss, target1, target2 = self.movement_model.levels(trade.entry, delta)
        trade.stop_loss = stop_loss
        trade.target1 = target1
        trade.target2 = target2

        risk = trade.entry - trade.stop_loss
        reward = trade.target1 - trade.entry
        trade.risk_reward = round(reward / risk, 2) if risk > 0 else 0
        return decision
