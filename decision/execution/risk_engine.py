from config.trading_config import TradingConfig


class RiskEngine:
    """
    Calculates premium-based risk.

    Responsibilities
    ----------------
    - Calculate Stop Loss
    - Calculate Risk / Reward

    Stop-loss percentage is determined
    using the implied volatility (IV) regime.

    Future Enhancements
    -------------------
    - ATR-aware stop loss
    - Gamma-aware stop loss
    - Market regime-aware stop loss
    """

    def build(self, decision, contract):
        """
        Populate stop loss and risk/reward
        for the selected trade.
        """

        if contract is None:
            return decision

        trade = decision.trade

        premium = contract.ltp

        # -------------------------------------
        # Invalid Premium
        # -------------------------------------

        if premium <= 0:
            trade.stop_loss = 0
            trade.risk_reward = 0
            return decision

        # -------------------------------------
        # Stop Loss
        # -------------------------------------

        risk_pct = self._risk_percent(contract.iv)

        trade.stop_loss = round(
            premium * (1 - risk_pct),
            2
        )

        # -------------------------------------
        # Validate Trade Levels
        # -------------------------------------

        if (
            trade.entry <= 0
            or trade.target1 <= trade.entry
        ):
            trade.risk_reward = 0
            return decision

        # -------------------------------------
        # Risk / Reward
        # -------------------------------------

        risk = trade.entry - trade.stop_loss
        reward = trade.target1 - trade.entry

        if risk <= 0:
            trade.risk_reward = 0
        else:
            trade.risk_reward = round(
                reward / risk,
                2
            )

        return decision

    # ==================================================
    # Private Methods
    # ==================================================

    def _risk_percent(self, iv):
        """
        Determine stop-loss percentage
        based on the IV regime.
        """

        if iv >= TradingConfig.HIGH_IV_THRESHOLD:
            return TradingConfig.STOPLOSS_HIGH_IV

        if iv <= TradingConfig.LOW_IV_THRESHOLD:
            return TradingConfig.STOPLOSS_LOW_IV

        return TradingConfig.STOPLOSS_NORMAL_IV