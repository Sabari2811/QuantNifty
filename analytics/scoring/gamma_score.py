class GammaScore:
    """Direction-aware gamma contribution for the NIFTY decision score."""

    MAX_SCORE = 15

    def calculate(self, dealer, signal):
        dealer = dealer or {}
        signal = signal or {}
        trade = signal.get("signal", "NO TRADE") if isinstance(signal, dict) else "NO TRADE"
        score = 0
        reasons = []

        dealer_gamma = dealer.get("dealer_gamma")
        gamma_flip = dealer.get("gamma_flip")
        total_gex = dealer.get("total_gex")

        if trade == "BUY CALL":
            if dealer_gamma == "LONG":
                score += 8
                reasons.append("Dealers Long Gamma")
            if gamma_flip is not None:
                score += 4
                reasons.append("Gamma Flip")
            if isinstance(total_gex, (int, float)) and total_gex > 0:
                score += 3
                reasons.append("Positive GEX")
        elif trade == "BUY PUT":
            if dealer_gamma == "SHORT":
                score += 8
                reasons.append("Dealers Short Gamma")
            if gamma_flip is not None:
                score += 4
                reasons.append("Gamma Flip")
            if isinstance(total_gex, (int, float)) and total_gex < 0:
                score += 3
                reasons.append("Negative GEX")
        else:
            if gamma_flip is not None:
                score += 3

        return {
            "score": min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "reasons": reasons,
        }
