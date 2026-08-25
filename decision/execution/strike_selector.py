class SmartStrikeSelector:
    """
    Selects the best option strike.

    Current Version:
    - BUY CALL → nearest valid resistance
    - BUY PUT  → nearest valid support

    Future:
    - ATM / ITM / OTM selection
    - Confidence-based selection
    - IV-aware selection
    """

    @staticmethod
    def _numeric_levels(levels):
        result = []
        for level in levels:
            if level is None:
                continue
            try:
                value = float(level)
            except (TypeError, ValueError):
                continue
            if value == value:
                result.append(value)
        return result

    def select(self, decision, snapshot):

        dealer = snapshot.dealer
        spot = float(snapshot.spot)

        if decision.signal.name == "BUY CALL":
            levels = self._numeric_levels([
                dealer.get("call_wall"),
                dealer.get("gamma_wall"),
            ])
            levels = [level for level in levels if level >= spot]
            if levels:
                return min(levels)
            return round(spot / 50) * 50

        if decision.signal.name == "BUY PUT":
            levels = self._numeric_levels([
                dealer.get("put_wall"),
                dealer.get("gamma_flip"),
            ])
            levels = [level for level in levels if level <= spot]
            if levels:
                return max(levels)
            return round(spot / 50) * 50

        return None
