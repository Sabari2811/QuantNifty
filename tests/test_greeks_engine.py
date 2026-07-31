import os
import sys
import traceback
from datetime import datetime, timedelta

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.greeks_engine import GreeksEngine


# ----------------------------------------------------------
# Helper
# ----------------------------------------------------------

def check(name, condition):

    if condition:
        print(f"✓ {name}")
    else:
        print(f"✗ {name}")
        raise AssertionError(name)


# ----------------------------------------------------------
# Validate Result Schema
# ----------------------------------------------------------

def validate_result(result):

    expected = [
        "iv",
        "delta",
        "gamma",
        "theta",
        "vega",
        "rho"
    ]

    for key in expected:

        check(f"{key} exists", key in result)


# ----------------------------------------------------------
# Test
# ----------------------------------------------------------

def run():

    print("=" * 70)
    print("Greeks Engine Test")
    print("=" * 70)

    engine = GreeksEngine()

    # ------------------------------------------------------
    # Time To Expiry
    # ------------------------------------------------------

    print("\n[1] Time To Expiry")

    expiry = datetime.now() + timedelta(days=7)

    t = engine.get_time_to_expiry(expiry)

    print("Years :", t)

    check("Positive Time", t > 0)

    # ------------------------------------------------------
    # CE Greeks
    # ------------------------------------------------------

    print("\n[2] CE Greeks")

    ce = engine.calculate_greeks(
        option_price=150,
        spot_price=25000,
        strike_price=25000,
        option_type="CE",
        time_to_expiry=t
    )

    print(ce)

    validate_result(ce)

    check("IV", ce["iv"] is not None)
    check("Delta", ce["delta"] is not None)
    check("Gamma", ce["gamma"] is not None)

    # ------------------------------------------------------
    # PE Greeks
    # ------------------------------------------------------

    print("\n[3] PE Greeks")

    pe = engine.calculate_greeks(
        option_price=150,
        spot_price=25000,
        strike_price=25000,
        option_type="PE",
        time_to_expiry=t
    )

    print(pe)

    validate_result(pe)

    check("PE IV", pe["iv"] is not None)

    # ------------------------------------------------------
    # Expiry String
    # ------------------------------------------------------

    print("\n[4] Expiry String")

    expiry_string = (
        datetime.now() + timedelta(days=10)
    ).strftime("%d/%m/%Y %H:%M")

    result = engine.calculate_greeks(
        option_price=200,
        spot_price=25000,
        strike_price=25100,
        option_type="CE",
        expiry=expiry_string
    )

    print(result)

    validate_result(result)

    # ------------------------------------------------------
    # Missing Expiry
    # ------------------------------------------------------

    print("\n[5] Missing Expiry")

    try:

        engine.calculate_greeks(
            option_price=100,
            spot_price=25000,
            strike_price=25000,
            option_type="CE"
        )

        raise Exception("Should fail")

    except ValueError:

        print("✓ Missing expiry validation")

    # ------------------------------------------------------
    # Expired Option
    # ------------------------------------------------------

    print("\n[6] Expired Option")

    expired = datetime.now() - timedelta(days=1)

    result = engine.calculate_greeks(
        option_price=50,
        spot_price=25000,
        strike_price=25000,
        option_type="CE",
        expiry=expired
    )

    print(result)

    validate_result(result)

    # ------------------------------------------------------
    # Invalid Price
    # ------------------------------------------------------

    print("\n[7] Invalid Price")

    result = engine.calculate_greeks(
        option_price=-1,
        spot_price=25000,
        strike_price=25000,
        option_type="CE",
        time_to_expiry=t
    )

    print(result)

    validate_result(result)

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


# ----------------------------------------------------------
# Entry
# ----------------------------------------------------------

if __name__ == "__main__":

    try:

        run()

    except Exception:

        print("\n" + "=" * 70)
        print("TEST FAILED")
        print("=" * 70)

        traceback.print_exc()