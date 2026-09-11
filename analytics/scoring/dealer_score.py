class DealerScore:
    """Direction-aware dealer contribution for the NIFTY decision score."""

    MAX_SCORE = 20

    def calculate(self, dealer, dealer_flow, signal):
        dealer = dealer or {}
        dealer_flow = dealer_flow or {}
        score = 0
        reasons = []
        trade = signal.get("signal", "NO TRADE") if isinstance(signal, dict) else "NO TRADE"

        dealer_gamma = dealer.get("dealer_gamma")
        market_mode = dealer.get("market_mode")
        dealer_delta = dealer_flow.get("dealer_delta")
        dealer_vanna = dealer_flow.get("dealer_vanna")
        dealer_charm = dealer_flow.get("dealer_charm")

        if trade == "BUY CALL":
            if dealer_gamma == "LONG":
                score += 6
                reasons.append("Dealers Long Gamma")
            if market_mode == "TRENDING":
                score += 4
                reasons.append("Trending Market")
            if dealer_delta == "LONG":
                score += 5
                reasons.append("Positive Delta")
            if dealer_vanna == "POSITIVE":
                score += 5
                reasons.append("Positive Vanna")

        elif trade == "BUY PUT":
            if dealer_gamma == "SHORT":
                score += 6
                reasons.append("Dealers Short Gamma")
            if market_mode == "TRENDING":
                score += 4
                reasons.append("Trending Market")
            if dealer_delta == "LONG":
                score += 5
                reasons.append("Dealers Hedging")
            if dealer_charm == "NEGATIVE":
                score += 5
                reasons.append("Negative Charm")

        else:
            if dealer_gamma == "LONG":
                score += 3
            if market_mode == "TRENDING":
                score += 2

        return {
            "score": min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "reasons": reasons,
        }
