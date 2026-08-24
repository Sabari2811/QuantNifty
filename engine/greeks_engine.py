from datetime import datetime
import math

from vollib.black_scholes.implied_volatility import implied_volatility
from vollib.black_scholes.greeks.analytical import (
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
        """Return exact fractional years until expiry using total seconds."""
        if isinstance(expiry, str):
            expiry = datetime.strptime(expiry, "%d/%m/%Y %H:%M")

        if not isinstance(expiry, datetime):
            raise TypeError("expiry must be a datetime or supported expiry string")

        now = datetime.now(expiry.tzinfo) if expiry.tzinfo else datetime.now()
        seconds = (expiry - now).total_seconds()

        if seconds <= 0:
            raise ValueError("expiry must be in the future")

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
                raise ValueError("Either expiry or time_to_expiry must be provided.")
            time_to_expiry = self.get_time_to_expiry(expiry)

        values = {
            "option_price": option_price,
            "spot_price": spot_price,
            "strike_price": strike_price,
            "time_to_expiry": time_to_expiry,
            "risk_free_rate": risk_free_rate,
        }
        for name, value in values.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be numeric") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"{name} must be finite")

        if float(option_price) <= 0:
            raise ValueError("option_price must be positive")
        if float(spot_price) <= 0:
            raise ValueError("spot_price must be positive")
        if float(strike_price) <= 0:
            raise ValueError("strike_price must be positive")
        if float(time_to_expiry) <= 0:
            raise ValueError("time_to_expiry must be positive")

        option_type = str(option_type).upper()
        if option_type not in {"CE", "PE"}:
            raise ValueError("option_type must be CE or PE")

        flag = "c" if option_type == "CE" else "p"

        try:
            iv = implied_volatility(
                option_price,
                spot_price,
                strike_price,
                time_to_expiry,
                risk_free_rate,
                flag,
            )
        except Exception as exc:
            raise ValueError(
                "Unable to solve implied volatility for the supplied option inputs"
            ) from exc

        return {
            "iv": iv,
            "delta": delta(
                flag, spot_price, strike_price, time_to_expiry,
                risk_free_rate, iv
            ),
            "gamma": gamma(
                flag, spot_price, strike_price, time_to_expiry,
                risk_free_rate, iv
            ),
            "theta": theta(
                flag, spot_price, strike_price, time_to_expiry,
                risk_free_rate, iv
            ),
            "vega": vega(
                flag, spot_price, strike_price, time_to_expiry,
                risk_free_rate, iv
            ),
            "rho": rho(
                flag, spot_price, strike_price, time_to_expiry,
                risk_free_rate, iv
            ),
        }
