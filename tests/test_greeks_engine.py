import os
import sys
import traceback
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.greeks_engine import GreeksEngine


def check(name, condition):
    if condition:
        print(f"✓ {name}")
    else:
        print(f"✗ {name}")
        raise AssertionError(name)


def test_ambiguous_provider_expiry_uses_future_interpretation():
    engine = GreeksEngine()
    target = datetime.now() + timedelta(days=7)

    # The same slash-formatted date can be represented by either convention.
    # The parser must select the interpretation that is actually future rather
    # than accepting the first syntactically valid interpretation.
    day_first = target.strftime("%d/%m/%Y %H:%M")
    month_first = target.strftime("%m/%d/%Y %H:%M")

    assert engine.get_time_to_expiry(day_first) > 0
    assert engine.get_time_to_expiry(month_first) > 0


def validate_result(result):
    for key in ["iv", "delta", "gamma", "theta", "vega", "rho"]:
        check(f"{key} exists", key in result)


def run():
    print("=" * 70)
    print("Greeks Engine Test")
    print("=" * 70)

    engine = GreeksEngine()

    print("\n[1] Time To Expiry")
    expiry = datetime.now() + timedelta(days=7)
    t = engine.get_time_to_expiry(expiry)
    print("Years :", t)
    check("Positive Time", t > 0)

    print("\n[2] CE Greeks")
    ce = engine.calculate_greeks(
        option_price=150,
        spot_price=25000,
        strike_price=25000,
        option_type="CE",
        time_to_expiry=t,
    )
    print(ce)
    validate_result(ce)
    check("IV", ce["iv"] is not None)
    check("Delta", ce["delta"] is not None)
    check("Gamma", ce["gamma"] is not None)

    print("\n[3] PE Greeks")
    pe = engine.calculate_greeks(
        option_price=150,
        spot_price=25000,
        strike_price=25000,
        option_type="PE",
        time_to_expiry=t,
    )
    print(pe)
    validate_result(pe)
    check("PE IV", pe["iv"] is not None)

    print("\n[4] Expiry String")
    expiry_string = (datetime.now() + timedelta(days=10)).strftime("%d/%m/%Y %H:%M")
    result = engine.calculate_greeks(
        option_price=200,
        spot_price=25000,
        strike_price=25100,
        option_type="CE",
        expiry=expiry_string,
    )
    print(result)
    validate_result(result)

    print("\n[5] Missing Expiry")
    try:
        engine.calculate_greeks(
            option_price=100,
            spot_price=25000,
            strike_price=25000,
            option_type="CE",
        )
        raise AssertionError("Missing expiry should fail")
    except ValueError:
        print("✓ Missing expiry validation")

    print("\n[6] Expired Option")
    try:
        engine.calculate_greeks(
            option_price=50,
            spot_price=25000,
            strike_price=25000,
            option_type="CE",
            expiry=datetime.now() - timedelta(days=1),
        )
        raise AssertionError("Expired option should fail")
    except ValueError:
        print("✓ Expired option validation")

    print("\n[7] Invalid Price")
    try:
        engine.calculate_greeks(
            option_price=-1,
            spot_price=25000,
            strike_price=25000,
            option_type="CE",
            time_to_expiry=t,
        )
        raise AssertionError("Invalid price should fail")
    except ValueError:
        print("✓ Invalid price validation")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run()
    except Exception:
        print("\n" + "=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        traceback.print_exc()
        raise
