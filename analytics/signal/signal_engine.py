from __future__ import annotations


class SignalEngine:
    """NIFTY-only directional signal engine.

    The signal answers one question first: what should NIFTY do next?
    Option selection happens downstream. A trade is emitted only when
    probability and independent market evidence agree on the same direction.
    """

    MIN_PROBABILITY = 70
    MIN_CONFIDENCE = 20

    @staticmethod
    def _text(payload, *keys, default="UNKNOWN"):
        if not isinstance(payload, dict):
            return default
        for key in keys:
            value = payload.get(key)
            if value is not None:
                return str(value).upper()
        return default

    @staticmethod
    def _number(payload, *keys, default=None):
        if not isinstance(payload, dict):
            return default
        for key in keys:
            value = payload.get(key)
            try:
                return float(value)
            except (TypeError, ValueError):
                continue
        return default

    def generate(
        self,
        dealer,
        probability,
        spot,
        market_structure=None,
        pcr=None,
        technical=None,
        oi_flow=None,
    ):
        """Return an authoritative NIFTY CALL/PUT/WAIT decision.

        ``market_structure``, ``pcr``, ``technical`` and ``oi_flow`` are
        optional for compatibility with historical callers. When supplied,
        they become confirmation evidence rather than separate trade engines.
        """
        dealer = dealer or {}
        probability = probability or {}
        market_structure = market_structure or {}
        pcr = pcr or {}
        technical = technical or {}
        oi_flow = oi_flow or {}

        bullish = self._number(probability, "bullish_probability", default=50.0)
        bearish = self._number(probability, "bearish_probability", default=50.0)
        confidence = self._number(probability, "confidence", default=abs(bullish - bearish))

        bullish_evidence = []
        bearish_evidence = []

        dealer_gamma = self._text(dealer, "dealer_gamma")
        if dealer_gamma == "LONG":
            bullish_evidence.append("Dealers Long Gamma")
        elif dealer_gamma == "SHORT":
            bearish_evidence.append("Dealers Short Gamma")

        structure_bias = self._text(market_structure, "bias")
        if structure_bias == "BULLISH":
            bullish_evidence.append("NIFTY Structure Bullish")
        elif structure_bias == "BEARISH":
            bearish_evidence.append("NIFTY Structure Bearish")

        pcr_bias = self._text(pcr, "sentiment", "bias")
        if pcr_bias == "BULLISH":
            bullish_evidence.append("NIFTY PCR Bullish")
        elif pcr_bias == "BEARISH":
            bearish_evidence.append("NIFTY PCR Bearish")

        ema = technical.get("ema", {}) if isinstance(technical, dict) else {}
        vwap = technical.get("vwap", {}) if isinstance(technical, dict) else {}
        rsi = technical.get("rsi", {}) if isinstance(technical, dict) else {}
        ema_trend = self._text(ema, "trend")
        vwap_position = self._text(vwap, "position")
        rsi_state = self._text(rsi, "state")
        if ema_trend in {"BULLISH", "STRONG_BULLISH"}:
            bullish_evidence.append("NIFTY EMA Bullish")
        elif ema_trend in {"BEARISH", "STRONG_BEARISH"}:
            bearish_evidence.append("NIFTY EMA Bearish")
        if vwap_position == "ABOVE":
            bullish_evidence.append("NIFTY Above VWAP")
        elif vwap_position == "BELOW":
            bearish_evidence.append("NIFTY Below VWAP")
        if rsi_state == "BULLISH":
            bullish_evidence.append("NIFTY RSI Bullish")
        elif rsi_state == "BEARISH":
            bearish_evidence.append("NIFTY RSI Bearish")

        oi_summary = oi_flow.get("summary", {}) if isinstance(oi_flow, dict) else {}
        oi_bias = self._text(oi_summary, "market_bias")
        if oi_bias == "BULLISH":
            bullish_evidence.append("NIFTY OI Flow Bullish")
        elif oi_bias == "BEARISH":
            bearish_evidence.append("NIFTY OI Flow Bearish")

        # Probability is the primary directional input. Additional evidence
        # can only confirm it; it can never manufacture a direction against
        # the probability engine.
        signal = "WAIT"
        reasons = list(probability.get("reasons", []))
        required = self.MIN_PROBABILITY
        if bullish >= required and bullish > bearish and confidence >= self.MIN_CONFIDENCE:
            confirmations = len(bullish_evidence)
            if confirmations >= 2 or not any((market_structure, pcr, technical, oi_flow)):
                signal = "BUY CALL"
                reasons.extend(bullish_evidence)
            else:
                reasons.append("NIFTY Bullish probability lacks confirmation")
        elif bearish >= required and bearish > bullish and confidence >= self.MIN_CONFIDENCE:
            confirmations = len(bearish_evidence)
            if confirmations >= 2 or not any((market_structure, pcr, technical, oi_flow)):
                signal = "BUY PUT"
                reasons.extend(bearish_evidence)
            else:
                reasons.append("NIFTY Bearish probability lacks confirmation")
        else:
            reasons.append("NIFTY probability/confidence below entry threshold")

        return {
            "signal": signal,
            "confidence": confidence,
            "spot": spot,
            "underlying": "NIFTY",
            "bullish_probability": bullish,
            "bearish_probability": bearish,
            "bullish_confirmations": len(bullish_evidence),
            "bearish_confirmations": len(bearish_evidence),
            "reasons": list(dict.fromkeys(reasons)),
        }
