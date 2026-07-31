import os
import sys
import traceback

# ----------------------------------------------------------
# Add Project Root to Python Path
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.instrument_manager import InstrumentManager


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
# Main Test
# ----------------------------------------------------------

def run():

    print("=" * 70)
    print("Instrument Manager Test")
    print("=" * 70)

    im = InstrumentManager()

    # ------------------------------------------------------
    # Download
    # ------------------------------------------------------

    print("\n[1] Download Instrument Masters")

    for source in ["index", "fno", "equity"]:

        try:
            im.download_instruments(source)
            print(f"Downloaded : {source}")

        except Exception as e:
            print(f"Skipped ({source}) : {e}")

    # ------------------------------------------------------
    # Load
    # ------------------------------------------------------

    print("\n[2] Load CSV")

    index_df = im.load_index()
    fno_df = im.load_fno()
    equity_df = im.load_equity()

    check("Index Loaded", not index_df.empty)
    check("FNO Loaded", not fno_df.empty)
    check("Equity Loaded", not equity_df.empty)

    # ------------------------------------------------------
    # Cache
    # ------------------------------------------------------

    print("\n[3] Cache")

    index_df2 = im.load_index()

    check(
        "Cache Working",
        id(index_df) == id(index_df2)
    )

    # ------------------------------------------------------
    # DataFrame Access
    # ------------------------------------------------------

    print("\n[4] get_dataframe()")

    df = im.get_dataframe("index")

    check(
        "get_dataframe()",
        not df.empty
    )

    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    print("\n[5] Search")

    result = im.search(
        "index",
        "NIFTY"
    )

    print(result.head())

    check(
        "Search Returned Rows",
        len(result) > 0
    )

    # ------------------------------------------------------
    # Scrip Code
    # ------------------------------------------------------

    print("\n[6] Scrip Code")

    code = im.get_scrip_code(
        "NSE",
        26000
    )

    print(code)

    check(
        "Scrip Code",
        code == "NSE_26000"
    )

    # ------------------------------------------------------
    # Options
    # ------------------------------------------------------

    print("\n[7] NIFTY Options")

    options = im.get_options("NIFTY")

    print("Rows :", len(options))

    check(
        "Options Found",
        not options.empty
    )

    # ------------------------------------------------------
    # Expiry Dates
    # ------------------------------------------------------

    print("\n[8] Expiry Dates")

    expiries = im.get_expiry_dates("NIFTY")

    print(expiries[:5])

    check(
        "Expiry Available",
        len(expiries) > 0
    )

    weekly = im.get_nearest_weekly_expiry("NIFTY")

    print("Nearest Weekly :", weekly)

    monthly = im.get_monthly_expiry("NIFTY")

    print("Monthly :", monthly)

    # ------------------------------------------------------
    # Option Lookup
    # ------------------------------------------------------

    print("\n[9] Option Lookup")

    sample = options.iloc[0]

    option = im.get_option(
        "NIFTY",
        sample["EXPIRY_DATE"],
        sample["STRIKE_PRICE"],
        sample["OPTION_TYPE"]
    )

    check(
        "Option Found",
        option is not None
    )

    print(option)

    # ------------------------------------------------------
    # Security ID
    # ------------------------------------------------------

    print("\n[10] Security ID")

    sid = im.get_security_id(
        "NIFTY",
        sample["EXPIRY_DATE"],
        sample["STRIKE_PRICE"],
        sample["OPTION_TYPE"]
    )

    print(sid)

    check(
        "Security ID",
        isinstance(sid, int)
    )

    # ------------------------------------------------------
    # Lot Size
    # ------------------------------------------------------

    print("\n[11] Lot Size")

    lot = im.get_lot_size("NIFTY")

    print(lot)

    check(
        "Lot Size",
        isinstance(lot, int)
    )

    # ------------------------------------------------------
    # Index Alias
    # ------------------------------------------------------

    print("\n[12] Index Alias Lookup")

    aliases = [
        "NIFTY",
        "NIFTY50",
        "BANKNIFTY",
        "BANK NIFTY",
        "FINNIFTY",
        "MIDCPNIFTY"
    ]

    for alias in aliases:

        sid = im.get_index_security_id(alias)

        print(f"{alias:<15} -> {sid}")

        check(
            alias,
            sid is not None
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