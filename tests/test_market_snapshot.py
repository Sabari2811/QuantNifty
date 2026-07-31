import os
import sys
import traceback
from datetime import datetime

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.market_snapshot import MarketSnapshot


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
# Test
# ----------------------------------------------------------

def run():

    print("=" * 70)
    print("Market Snapshot Test")
    print("=" * 70)

    snapshot = MarketSnapshot()

    # ------------------------------------------------------
    # Default Values
    # ------------------------------------------------------

    print("\n[1] Default Values")

    check("Default Symbol", snapshot.symbol == "NIFTY")
    check("Default Spot", snapshot.spot == 0.0)
    check("Default Future", snapshot.future == 0.0)
    check("Default Expiry", snapshot.expiry == "")
    check("Default VIX", snapshot.india_vix == 0.0)
    check("Timestamp None", snapshot.timestamp is None)

    # ------------------------------------------------------
    # Update
    # ------------------------------------------------------

    print("\n[2] Update Snapshot")

    snapshot.update(
        symbol="BANKNIFTY",
        spot=56520.75,
        future=56555.40,
        expiry="31/12/2026 15:30",
        india_vix=14.85
    )

    check("Updated Symbol", snapshot.symbol == "BANKNIFTY")
    check("Updated Spot", snapshot.spot == 56520.75)
    check("Updated Future", snapshot.future == 56555.40)
    check("Updated Expiry", snapshot.expiry == "31/12/2026 15:30")
    check("Updated VIX", snapshot.india_vix == 14.85)
    check("Timestamp Generated", isinstance(snapshot.timestamp, datetime))

    # ------------------------------------------------------
    # Dictionary Conversion
    # ------------------------------------------------------

    print("\n[3] Dictionary")

    data = snapshot.to_dict()

    print(data)

    expected_keys = [
        "symbol",
        "spot",
        "future",
        "expiry",
        "india_vix",
        "timestamp"
    ]

    for key in expected_keys:
        check(f"{key} exists", key in data)

    check("Dict Symbol", data["symbol"] == "BANKNIFTY")
    check("Dict Spot", data["spot"] == 56520.75)
    check("Dict Future", data["future"] == 56555.40)
    check("Dict Expiry", data["expiry"] == "31/12/2026 15:30")
    check("Dict VIX", data["india_vix"] == 14.85)
    check("Dict Timestamp", isinstance(data["timestamp"], datetime))

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