from datetime import datetime

from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import (
    delta,
    gamma,
    theta,
    vega,
    rho,
)


class GreeksEngine:

    def __init__(self, risk_free_rate=0.06):
        self.r = risk_free_rate

    # -------------------------------------------------------
    # Convert expiry datetime to years
    # -------------------------------------------------------

    def get_time_to_expiry(self, expiry):

        if isinstance(expiry, str):
            expiry = datetime.strptime(
                expiry,
                "%d/%m/%Y %H:%M"
            )

        seconds = (expiry - datetime.now()).total_seconds()

        if seconds <= 0:
            seconds = 1

        return seconds / (365 * 24 * 60 * 60)

    # -------------------------------------------------------
    # Main Greeks Calculator
    # -------------------------------------------------------

    def calculate_greeks(
        self,
        option_price,
        spot_price,
        strike_price,
        option_type,
        expiry=None,
        time_to_expiry=None,
        risk_free_rate=None
    ):

        if risk_free_rate is None:
            risk_free_rate = self.r

        if time_to_expiry is None:

            if expiry is None:
                raise ValueError(
                    "Either expiry or time_to_expiry must be provided."
                )

            time_to_expiry = self.get_time_to_expiry(expiry)

        flag = "c" if option_type.upper() == "CE" else "p"

        try:

            iv = implied_volatility(
                option_price,
                spot_price,
                strike_price,
                time_to_expiry,
                risk_free_rate,
                flag
            )

            return {

                "iv": iv,

                "delta": delta(
                    flag,
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    iv
                ),

                "gamma": gamma(
                    flag,
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    iv
                ),

                "theta": theta(
                    flag,
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    iv
                ),

                "vega": vega(
                    flag,
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    iv
                ),

                "rho": rho(
                    flag,
                    spot_price,
                    strike_price,
                    time_to_expiry,
                    risk_free_rate,
                    iv
                )

            }

        except Exception:

            return {

                "iv": None,
                "delta": None,
                "gamma": None,
                "theta": None,
                "vega": None,
                "rho": None

            }