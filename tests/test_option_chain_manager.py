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

from engine.option_chain_manager import OptionChainManager


# ----------------------------------------------------------
# Mock Instrument Manager
# ----------------------------------------------------------

class MockInstrumentManager:

    def get_nearest_weekly_expiry(self, symbol):

        return "07/21/2026 14:00"


# ----------------------------------------------------------
# Mock Strike Selector
# ----------------------------------------------------------

class MockStrikeSelector:

    def get_option_security_ids(
        self,
        symbol,
        expiry,
        spot_price,
        levels
    ):

        return [

            {
                "strike": 25000,
                "CE_ID": 111,
                "PE_ID": 222
            },

            {
                "strike": 25100,
                "CE_ID": 333,
                "PE_ID": 444
            }

        ]


# ----------------------------------------------------------
# Mock Provider
# ----------------------------------------------------------

class MockProvider:

    def get_quotes(self, security_ids):

        return {

            "NFO_111": {
                "live_price": 120.5,
                "open_interest": 50000,
                "volume": 1200
            },

            "NFO_222": {
                "live_price": 95.2,
                "open_interest": 47000,
                "volume": 900
            },

            "NFO_333": {
                "live_price": 82.3,
                "open_interest": 36000,
                "volume": 600
            },

            "NFO_444": {
                "live_price": 150.8,
                "open_interest": 54000,
                "volume": 1500
            }

        }


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
    print("Option Chain Manager Test")
    print("=" * 70)

    manager = OptionChainManager(
        provider=MockProvider(),
        strike_selector=MockStrikeSelector(),
        instrument_manager=MockInstrumentManager(),
        market_manager=None
    )

    df = manager.get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=2
    )

    print(df)

    # ------------------------------------------------------
    # Basic Checks
    # ------------------------------------------------------

    check("DataFrame", not df.empty)

    check("Rows", len(df) == 2)

    expected_columns = [

        "Strike",

        "CE_ID",
        "CE_LTP",
        "CE_OI",
        "CE_VOLUME",

        "PE_ID",
        "PE_LTP",
        "PE_OI",
        "PE_VOLUME"

    ]

    for col in expected_columns:

        check(f"Column {col}", col in df.columns)

    # ------------------------------------------------------
    # First Row
    # ------------------------------------------------------

    row = df.iloc[0]

    check("Strike", row["Strike"] == 25000)
    check("CE_ID", row["CE_ID"] == 111)
    check("PE_ID", row["PE_ID"] == 222)

    check("CE_LTP", row["CE_LTP"] == 120.5)
    check("PE_LTP", row["PE_LTP"] == 95.2)

    check("CE_OI", row["CE_OI"] == 50000)
    check("PE_OI", row["PE_OI"] == 47000)

    check("CE_VOLUME", row["CE_VOLUME"] == 1200)
    check("PE_VOLUME", row["PE_VOLUME"] == 900)

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