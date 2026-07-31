import os
import sys
import traceback

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.strike_selector import StrikeSelector


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
# Mock Instrument Manager
# ----------------------------------------------------------

class MockInstrumentManager:

    def get_option(
        self,
        symbol,
        expiry,
        strike,
        option_type
    ):

        # Simulate one missing contract
        if strike == 25150.0 and option_type == "CE":
            return None

        security_id = int(strike)

        if option_type == "PE":
            security_id += 100000

        return {
            "SECURITY_ID": security_id
        }


# ----------------------------------------------------------
# Test
# ----------------------------------------------------------

def run():

    print("=" * 70)
    print("Strike Selector Test")
    print("=" * 70)

    selector = StrikeSelector(
        MockInstrumentManager()
    )

    # ------------------------------------------------------
    # ATM Strike
    # ------------------------------------------------------

    atm = selector.get_atm_strike(25037)

    print("ATM :", atm)

    check(
        "ATM Strike",
        atm == 25050
    )

    # ------------------------------------------------------
    # Surrounding Strikes
    # ------------------------------------------------------

    strikes = selector.get_surrounding_strikes(
        spot_price=25037,
        levels=2
    )

    print(strikes)

    expected = [
        24950,
        25000,
        25050,
        25100,
        25150
    ]

    check(
        "Strike Range",
        strikes == expected
    )

    # ------------------------------------------------------
    # Option Security IDs
    # ------------------------------------------------------

    contracts = selector.get_option_security_ids(

        symbol="NIFTY",

        expiry="31/12/2026 15:30",

        spot_price=25037,

        levels=2

    )

    print()

    for row in contracts:
        print(row)

    # One strike is skipped because CE is missing
    check(
        "Contract Count",
        len(contracts) == 4
    )

    first = contracts[0]

    check(
        "Strike",
        first["strike"] == 24950
    )

    check(
        "CE_ID",
        first["CE_ID"] == 24950
    )

    check(
        "PE_ID",
        first["PE_ID"] == 124950
    )

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