class ExitEngine:
    """
    Determines whether a paper trade
    should be closed.

    Does NOT close the trade.
    It only returns the exit decision.
    """

    def evaluate(self, position):

        price = position.current_price

        # -------------------------------
        # Stop Loss
        # -------------------------------

        if price <= position.stop_loss:

            return {
                "exit": True,
                "reason": "STOP LOSS",
                "price": position.stop_loss,
            }

        # -------------------------------
        # Target
        # -------------------------------

        if price >= position.target:

            return {
                "exit": True,
                "reason": "TARGET",
                "price": position.target,
            }

        # -------------------------------
        # Hold
        # -------------------------------

        return {
            "exit": False,
            "reason": "",
            "price": 0,
        }