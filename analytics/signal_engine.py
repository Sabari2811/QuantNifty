class SignalEngine:
    """
    QuantNifty Signal Engine v1
    """

    def generate(

        self,

        dealer,

        probability,

        spot

    ):

        bullish = probability["bullish_probability"]

        bearish = probability["bearish_probability"]

        confidence = probability["confidence"]

        signal = "WAIT"

        reasons = []

        # ===========================================
        # BUY CALL
        # ===========================================

        if (

            dealer.dealer_gamma == "LONG"

            and

            bullish >= 70

        ):

            signal = "BUY CALL"

            reasons.append("Dealers Long Gamma")

            reasons.append("Bullish Probability High")

        # ===========================================
        # BUY PUT
        # ===========================================

        elif (

            dealer.dealer_gamma == "SHORT"

            and

            bearish >= 70

        ):

            signal = "BUY PUT"

            reasons.append("Dealers Short Gamma")

            reasons.append("Bearish Probability High")

        # ===========================================
        # WAIT
        # ===========================================

        else:

            signal = "WAIT"

            reasons.append("No High Probability Setup")

        return {

            "signal": signal,

            "confidence": confidence,

            "spot": spot,

            "reasons": reasons

        }