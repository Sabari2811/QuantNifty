from __future__ import annotations


class SignalEngine:
    """NIFTY-only directional signal engine.

    The signal answers one question first: what should NIFTY do next?
    Option selection happens downstream. A trade is emitted only when
    probability and independent market evidence agree on the same direction.
    """

    MIN_PROBABILITY = 70
    MIN_CONFIDENCE = 20
    MIN_CONFIRMATIONS = 2

    @staticmethod
    def _number(payload, key, default):
        try:
            return float(payload.get(key, default))
        except (TypeError, ValueError, AttributeError):
            return float(default)

    def generate(self, dealer, probability, spot, market_structure=None, pcr=None, technical=None, oi_flow=None):
        dealer = dealer or {}
        probability = probability or {}
        market_structure = market_structure or {}
        pcr = pcr or {}
        technical = technical or {}
        oi_flow = oi_flow or {}

        bullish = self._number(probability, "bullish_probability", 50)
        bearish = self._number(probability, "bearish_probability", 50)
        confidence = self._number(probability, "confidence", abs(bullish - bearish))

        bullish_evidence = []
        bearish_evidence = []

        if str(dealer.get("dealer_gamma", "")).upper() == "LONG":
            bullish_evidence.append("Dealers Long Gamma")
        elif str(dealer.get("dealer_gamma", "")).upper() == "SHORT":
            bearish_evidence.append("Dealers Short Gamma")

        if str(market_structure.get("bias", "")).upper() == "BULLISH":
            bullish_evidence.append("NIFTY Structure Bullish")
        elif str(market_structure.get("bias", "")).upper() == "BEARISH":
            bearish_evidence.append("NIFTY Structure Bearish")

        pcr_bias = str(pcr.get("sentiment", pcr.get("bias", ""))).upper()
        if pcr_bias == "BULLISH":
            bullish_evidence.append("NIFTY PCR Bullish")
        elif pcr_bias == "BEARISH":
            bearish_evidence.append("NIFTY PCR Bearish")

        ema = technical.get("ema", {}) if isinstance(technical, dict) else {}
        vwap = technical.get("vwap", {}) if isinstance(technical, dict) else {}
        rsi = technical.get("rsi", {}) if isinstance(technical, dict) else {}
        ema_trend = str(ema.get("trend", "")).upper()
        if ema_trend in {"BULLISH", "STRONG_BULLISH"}:
            bullish_evidence.append("NIFTY EMA Bullish")
        elif ema_trend in {"BEARISH", "STRONG_BEARISH"}:
            bearish_evidence.append("NIFTY EMA Bearish")
        vwap_position = str(vwap.get("position", "")).upper()
        if vwap_position == "ABOVE":
            bullish_evidence.append("NIFTY Above VWAP")
        elif vwap_position == "BELOW":
            bearish_evidence.append("NIFTY Below VWAP")
        rsi_state = str(rsi.get("state", "")).upper()
        if rsi_state == "BULLISH":
            bullish_evidence.append("NIFTY RSI Bullish")
        elif rsi_state == "BEARISH":
            bearish_evidence.append("NIFTY RSI Bearish")

        oi_summary = oi_flow.get("summary", {}) if isinstance(oi_flow, dict) else {}
        oi_bias = str(oi_summary.get("market_bias", "")).upper()
        if oi_bias == "BULLISH":
            bullish_evidence.append("NIFTY OI Flow Bullish")
        elif oi_bias == "BEARISH":
            bearish_evidence.append("NIFTY OI Flow Bearish")

        # ProbabilityEngine supplies the canonical confirmation count. For
        # legacy callers that do not provide it, dealer evidence is the minimum
        # compatibility fallback; live pipeline always provides the count.
        bullish_confirmations = int(probability.get("bullish_confirmations", len(bullish_evidence) if bullish_evidence else 0))
        bearish_confirmations = int(probability.get("bearish_confirmations", len(bearish_evidence) if bearish_evidence else 0))

        signal = "WAIT"
        reasons = list(probability.get("reasons", []))
        if bullish >= self.MIN_PROBABILITY and bullish > bearish and confidence >= self.MIN_CONFIDENCE:
            if bullish_confirmations >= self.MIN_CONFIRMATIONS:
                signal = "BUY CALL"
                reasons.extend(bullish_evidence)
            else:
                reasons.append("NIFTY bullish setup lacks directional confluence")
        elif bearish >= self.MIN_PROBABILITY and bearish > bullish and confidence >= self.MIN_CONFIDENCE:
            if bearish_confirmations >= self.MIN_CONFIRMATIONS:
                signal = "BUY PUT"
                reasons.extend(bearish_evidence)
            else:
                reasons.append("NIFTY bearish setup lacks directional confluence")
        else:
            reasons.append("NIFTY probability/confidence below entry threshold")

        return {
            "signal": signal,
            "confidence": confidence,
            "spot": spot,
            "underlying": "NIFTY",
            "bullish_probability": bullish,
            "bearish_probability": bearish,
            "bullish_confirmations": bullish_confirmations,
            "bearish_confirmations": bearish_confirmations,
            "reasons": list(dict.fromkeys(reasons)),
        }
