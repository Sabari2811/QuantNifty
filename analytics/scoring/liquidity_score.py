class LiquidityScore:
    """Direction-aware liquidity contribution for the NIFTY decision score."""

    MAX_SCORE = 15

    def calculate(self, liquidity, signal, spot):
        liquidity = liquidity or {}
        signal = signal or {}
        trade = signal.get("signal", "NO TRADE") if isinstance(signal, dict) else "NO TRADE"
        score = 0
        reasons = []

        support = liquidity.get("support")
        resistance = liquidity.get("resistance")
        absorption = liquidity.get("absorption") or {}
        imbalance = liquidity.get("order_imbalance") or {}
        buy_pressure = bool(imbalance.get("buy_pressure"))
        sell_pressure = bool(imbalance.get("sell_pressure"))
        absorption_count = absorption.get("count", 0) or 0

        if trade == "BUY CALL":
            if support is not None and spot > support:
                score += 5
                reasons.append("Above Support")
            if absorption_count > 0:
                score += 5
                reasons.append("Institutional Absorption")
            if buy_pressure:
                score += 5
                reasons.append("Buy Pressure")
        elif trade == "BUY PUT":
            if resistance is not None and spot < resistance:
                score += 5
                reasons.append("Below Resistance")
            if absorption_count > 0:
                score += 5
                reasons.append("Institutional Absorption")
            if sell_pressure:
                score += 5
                reasons.append("Sell Pressure")
        else:
            if absorption_count > 0:
                score += 3

        return {
            "score": min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "reasons": reasons,
        }
