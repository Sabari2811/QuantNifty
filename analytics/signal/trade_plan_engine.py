class TradePlanEngine:
    """
    QuantNifty Trade Plan Engine V4

    Generates a complete trade plan using

    • Signal
    • Dealer Analytics
    • ATR
    • Smart Strike
    """

    def generate(

        self,

        signal,

        dealer,

        spot,

        atr,

        smart_strike

    ):

        atr_value = atr.get("atr", 50)

        trade = {

            "signal": signal["signal"],

            "recommended_strike": smart_strike["strike"],

            "option_type": smart_strike["option_type"],

            "strike_score": smart_strike["score"],

            "delta": smart_strike["delta"],

            "iv": smart_strike["iv"],

            "gex": smart_strike["gex"],

            "entry": None,

            "stop_loss": None,

            "target1": None,

            "target2": None,

            "risk_reward": None,

            "atr": atr_value,

            "volatility": atr["volatility"],

            "reasons": []

        }

        signal_name = signal["signal"]

        # =====================================================
        # BUY CALL
        # =====================================================

        if signal_name == "BUY CALL":

            if dealer["gamma_flip"] is not None:

                entry = dealer["gamma_flip"] + 5

                trade["reasons"].append(
                    "Entry above Gamma Flip"
                )

            else:

                entry = spot + 5

                trade["reasons"].append(
                    "Entry above Spot"
                )

            trade["entry"] = round(entry, 2)

            trade["stop_loss"] = round(
                entry - atr_value,
                2
            )

            trade["target1"] = round(
                entry + (1.5 * atr_value),
                2
            )

            trade["target2"] = round(
                entry + (3 * atr_value),
                2
            )

        # =====================================================
        # BUY PUT
        # =====================================================

        elif signal_name == "BUY PUT":

            if dealer["gamma_flip"] is not None:

                entry = dealer["gamma_flip"] - 5

                trade["reasons"].append(
                    "Entry below Gamma Flip"
                )

            else:

                entry = spot - 5

                trade["reasons"].append(
                    "Entry below Spot"
                )

            trade["entry"] = round(entry, 2)

            trade["stop_loss"] = round(
                entry + atr_value,
                2
            )

            trade["target1"] = round(
                entry - (1.5 * atr_value),
                2
            )

            trade["target2"] = round(
                entry - (3 * atr_value),
                2
            )

        # =====================================================
        # WAIT
        # =====================================================

        else:

            trade["recommended_strike"] = "-"

            trade["option_type"] = "-"

            trade["strike_score"] = 0

            trade["entry"] = "-"

            trade["stop_loss"] = "-"

            trade["target1"] = "-"

            trade["target2"] = "-"

            trade["risk_reward"] = "-"

            trade["reasons"].append(
                "No trade available"
            )

            return trade

        # =====================================================
        # Risk Reward
        # =====================================================

        risk = abs(

            trade["entry"]

            -

            trade["stop_loss"]

        )

        reward = abs(

            trade["target2"]

            -

            trade["entry"]

        )

        rr = round(

            reward / risk,

            2

        ) if risk else 0

        trade["risk_reward"] = f"1 : {rr}"

        # =====================================================
        # Smart Strike Reasons
        # =====================================================

        trade["reasons"].extend(

            smart_strike["reasons"]

        )

        # =====================================================
        # Dealer Context
        # =====================================================

        trade["reasons"].append(

            f"Dealer : {dealer['dealer_gamma']}"

        )

        trade["reasons"].append(

            f"Market : {dealer['market_mode']}"

        )

        trade["reasons"].append(

            f"ATR : {atr['volatility']}"

        )

        return trade