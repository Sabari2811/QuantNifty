import math
from datetime import datetime, timedelta

import pytest

from engine.greeks_engine import GreeksEngine


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _reference(S, K, T, r, sigma, flag):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    pdf = _norm_pdf(d1)

    if flag == "c":
        price = S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
        delta = _norm_cdf(d1)
        rho = K * T * math.exp(-r * T) * _norm_cdf(d2) * 0.01
        theta_annual = (
            -(S * pdf * sigma) / (2.0 * math.sqrt(T))
            - r * K * math.exp(-r * T) * _norm_cdf(d2)
        )
    else:
        price = K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)
        delta = _norm_cdf(d1) - 1.0
        rho = -K * T * math.exp(-r * T) * _norm_cdf(-d2) * 0.01
        theta_annual = (
            -(S * pdf * sigma) / (2.0 * math.sqrt(T))
            + r * K * math.exp(-r * T) * _norm_cdf(-d2)
        )

    gamma = pdf / (S * sigma * math.sqrt(T))
    vega = S * pdf * math.sqrt(T) * 0.01
    theta = theta_annual / 365.0

    return price, delta, gamma, theta, vega, rho


@pytest.mark.parametrize("option_type, flag", [("CE", "c"), ("PE", "p")])
def test_greeks_match_independent_black_scholes_reference(option_type, flag):
    engine = GreeksEngine(risk_free_rate=0.06)
    S, K, T, r, sigma = 25000.0, 25100.0, 30.0 / 365.0, 0.06, 0.20
    price, delta, gamma, theta, vega, rho = _reference(S, K, T, r, sigma, flag)

    result = engine.calculate_greeks(
        option_price=price,
        spot_price=S,
        strike_price=K,
        option_type=option_type,
        time_to_expiry=T,
        risk_free_rate=r,
    )

    assert result["iv"] == pytest.approx(sigma, rel=1e-5, abs=1e-7)
    assert result["delta"] == pytest.approx(delta, rel=1e-5, abs=1e-7)
    assert result["gamma"] == pytest.approx(gamma, rel=1e-5, abs=1e-10)
    assert result["theta"] == pytest.approx(theta, rel=1e-5, abs=1e-7)
    assert result["vega"] == pytest.approx(vega, rel=1e-5, abs=1e-7)
    assert result["rho"] == pytest.approx(rho, rel=1e-5, abs=1e-7)


def test_time_to_expiry_preserves_fractional_day():
    engine = GreeksEngine()
    expiry = datetime.now() + timedelta(days=1, hours=12)
    result = engine.get_time_to_expiry(expiry)
    assert result == pytest.approx(1.5 / 365.0, rel=2e-4)


def test_provider_month_first_expiry_format_is_supported():
    engine = GreeksEngine()
    expiry = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y %H:%M")
    result = engine.get_time_to_expiry(expiry)
    assert result > 0


def test_expired_expiry_is_rejected():
    with pytest.raises(ValueError, match="expiry must be in the future"):
        GreeksEngine().get_time_to_expiry(datetime.now() - timedelta(seconds=1))


@pytest.mark.parametrize(
    "field,value",
    [
        ("option_price", 0),
        ("spot_price", 0),
        ("strike_price", 0),
        ("time_to_expiry", 0),
    ],
)
def test_invalid_positive_inputs_are_rejected(field, value):
    kwargs = dict(
        option_price=150,
        spot_price=25000,
        strike_price=25000,
        option_type="CE",
        time_to_expiry=30 / 365,
    )
    kwargs[field] = value
    with pytest.raises(ValueError):
        GreeksEngine().calculate_greeks(**kwargs)


def test_invalid_option_type_is_rejected():
    with pytest.raises(ValueError, match="option_type must be CE or PE"):
        GreeksEngine().calculate_greeks(
            option_price=150,
            spot_price=25000,
            strike_price=25000,
            option_type="XX",
            time_to_expiry=30 / 365,
        )


def test_implied_volatility_failure_is_explicit():
    # Price below intrinsic value cannot have a Black-Scholes implied volatility.
    with pytest.raises(ValueError, match="Unable to solve implied volatility"):
        GreeksEngine().calculate_greeks(
            option_price=1,
            spot_price=25000,
            strike_price=20000,
            option_type="CE",
            time_to_expiry=30 / 365,
        )
