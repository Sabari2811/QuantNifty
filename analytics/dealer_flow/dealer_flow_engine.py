class DealerFlowEngine:
    """
    Dealer Flow Analytics

    Combines

        Delta Exposure
        Vanna Exposure
        Charm Exposure

    Returns dealer positioning.
    """

    def analyze(

        self,

        delta_summary,

        vanna_summary,

        charm_summary

    ):

        total_dex = delta_summary["total_dex"]

        total_vanna = vanna_summary["total_vanna"]

        total_charm = charm_summary["total_charm"]

        # ----------------------------------------
        # Dealer Direction
        # ----------------------------------------

        dealer_delta = (

            "LONG"

            if total_dex >= 0

            else "SHORT"

        )

        dealer_vanna = (

            "POSITIVE"

            if total_vanna >= 0

            else "NEGATIVE"

        )

        dealer_charm = (

            "POSITIVE"

            if total_charm >= 0

            else "NEGATIVE"

        )

        # ----------------------------------------
        # Dealer Pressure
        # ----------------------------------------

        score = 0

        if total_dex > 0:
            score += 1
        else:
            score -= 1

        if total_vanna > 0:
            score += 1
        else:
            score -= 1

        if total_charm > 0:
            score += 1
        else:
            score -= 1

        if score >= 2:

            pressure = "BUY"

            hedge = "BUY DIPS"

        elif score <= -2:

            pressure = "SELL"

            hedge = "SELL RALLIES"

        else:

            pressure = "NEUTRAL"

            hedge = "DELTA HEDGE"

        # ----------------------------------------
        # Flip Probability
        # ----------------------------------------

        flip_probability = min(

            100,

            int(abs(score) * 33)

        )

        return {

            "dealer_delta": dealer_delta,

            "dealer_vanna": dealer_vanna,

            "dealer_charm": dealer_charm,

            "dealer_pressure": pressure,

            "dealer_hedging": hedge,

            "flip_probability": flip_probability,

            "total_dex": total_dex,

            "total_vanna": total_vanna,

            "total_charm": total_charm

        }