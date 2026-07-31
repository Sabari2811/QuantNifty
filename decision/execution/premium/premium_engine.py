from config.trading_config import TradingConfig


class PremiumEngine:
    """
    Builds premium-based trade levels.

    Responsibilities
    ----------------
    - Calculate Entry Premium
    - Calculate Target 1
    - Calculate Target 2

    Stop Loss:
        Handled by RiskEngine.

    Future Enhancements
    -------------------
    - ATR-based Targets
    - Expected Move Targets
    - Gamma Wall Targets
    """

    def build(self, decision, contract):
        """
        Populate premium-based trade levels.
        """

        if contract is None:
            return decision

        trade = decision.trade

        premium = contract.ltp

        # -------------------------------------
        # Invalid Premium
        # -------------------------------------

        if premium <= 0:

            trade.entry = 0
            trade.target1 = 0
            trade.target2 = 0

            return decision

        # -------------------------------------
        # Entry
        # -------------------------------------

        trade.entry = round(
            premium,
            2
        )

        # -------------------------------------
        # Targets
        # -------------------------------------

        trade.target1 = round(
            premium *
            TradingConfig.TARGET1_MULTIPLIER,
            2
        )

        trade.target2 = round(
            premium *
            TradingConfig.TARGET2_MULTIPLIER,
            2
        )

        return decision