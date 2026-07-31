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

from engine.market_data_manager import MarketDataManager


# ----------------------------------------------------------
# Mock Provider
# ----------------------------------------------------------

class MockProvider:

    def get_index_quote(self, symbol):

        data = {
            "NIFTY 50": {"ltp": 25250.45},
            "NIFTY BANK": {"LTP": 57321.80},
            "NIFTY FIN SERVICE": {"last_price": 28115.15},
            "NIFTY MID SELECT": {"lastPrice": 14205.60},
        }

        return data.get(symbol)

    def get_quote(self, symbol):

        return {
            "symbol": symbol,
            "price": 100
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
    print("Market Data Manager Test")
    print("=" * 70)

    provider = MockProvider()

    mdm = MarketDataManager(provider)

    # ------------------------------------------------------
    # Spot Price
    # ------------------------------------------------------

    print("\n[1] Spot Price")

    nifty = mdm.get_spot_price("NIFTY")
    bank = mdm.get_spot_price("BANKNIFTY")
    fin = mdm.get_spot_price("FINNIFTY")
    mid = mdm.get_spot_price("MIDCPNIFTY")

    print("NIFTY      :", nifty)
    print("BANKNIFTY  :", bank)
    print("FINNIFTY   :", fin)
    print("MIDCPNIFTY :", mid)

    check("NIFTY", nifty == 25250.45)
    check("BANKNIFTY", bank == 57321.80)
    check("FINNIFTY", fin == 28115.15)
    check("MIDCPNIFTY", mid == 14205.60)

    # ------------------------------------------------------
    # Unsupported Symbol
    # ------------------------------------------------------

    print("\n[2] Unsupported Symbol")

    try:

        mdm.get_spot_price("SENSEX")

        raise Exception("Should have failed")

    except ValueError:

        print("✓ Unsupported Symbol")

    # ------------------------------------------------------
    # Generic Quote
    # ------------------------------------------------------

    print("\n[3] Generic Quote")

    quote = mdm.get_quote("RELIANCE")

    print(quote)

    check(
        "Generic Quote",
        quote["symbol"] == "RELIANCE"
    )

    # ------------------------------------------------------
    # Cache
    # ------------------------------------------------------

    print("\n[4] Cache")

    mdm.set_cache("spot", 25250.45)

    check(
        "Cache Set/Get",
        mdm.get_cache("spot") == 25250.45
    )

    check(
        "Missing Cache",
        mdm.get_cache("dummy") is None
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