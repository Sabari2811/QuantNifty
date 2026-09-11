class StructureScore:
    """Direction-aware market-structure contribution for the NIFTY decision score."""

    MAX_SCORE = 10

    def calculate(self, market_structure, pcr, expected_move, signal, spot):
        market_structure = market_structure or {}
        pcr = pcr or {}
        expected_move = expected_move or {}
        signal = signal or {}
        trade = signal.get("signal", "NO TRADE") if isinstance(signal, dict) else "NO TRADE"
        score = 0
        reasons = []

        bias = market_structure.get("bias")
        structure = market_structure.get("structure")
        oi_pcr = pcr.get("oi_pcr")
        upper = expected_move.get("upper")
        lower = expected_move.get("lower")

        if trade == "BUY CALL":
            if bias == "BULLISH":
                score += 4
                reasons.append("Bullish Structure")
            if isinstance(oi_pcr, (int, float)) and oi_pcr > 1:
                score += 3
                reasons.append("Bullish PCR")
            if isinstance(upper, (int, float)) and spot < upper:
                score += 3
                reasons.append("Inside Expected Move")
        elif trade == "BUY PUT":
            if bias == "BEARISH":
                score += 4
                reasons.append("Bearish Structure")
            if isinstance(oi_pcr, (int, float)) and oi_pcr < 1:
                score += 3
                reasons.append("Bearish PCR")
            if isinstance(lower, (int, float)) and spot > lower:
                score += 3
                reasons.append("Inside Expected Move")
        else:
            if structure == "RANGING":
                score += 2

        return {
            "score": min(score, self.MAX_SCORE),
            "max_score": self.MAX_SCORE,
            "reasons": reasons,
        }
