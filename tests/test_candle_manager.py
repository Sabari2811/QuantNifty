import os
import sys
import traceback
import pandas as pd

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.candle_manager import CandleManager


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
    print("Candle Manager Test")
    print("=" * 70)

    manager = CandleManager()

    # ------------------------------------------------------
    # Empty Input
    # ------------------------------------------------------

    print("\n[1] Empty Candle List")

    df = manager.to_dataframe([])

    check("Empty DataFrame", df.empty)

    expected_columns = [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    check(
        "Standard Columns",
        list(df.columns) == expected_columns
    )

    # ------------------------------------------------------
    # Sample Candles (intentionally unsorted)
    # ------------------------------------------------------

    print("\n[2] Convert Candle List")

    candles = [

        {
            "ts": 1752566520,
            "o": 25260,
            "h": 25280,
            "l": 25250,
            "c": 25270,
            "v": 1800
        },

        {
            "ts": 1752566460,
            "o": 25240,
            "h": 25265,
            "l": 25230,
            "c": 25260,
            "v": 1500
        },

        {
            "ts": 1752566580,
            "o": 25270,
            "h": 25290,
            "l": 25260,
            "c": 25285,
            "v": 2100
        }

    ]

    df = manager.to_dataframe(candles)

    print(df)

    # ------------------------------------------------------
    # Basic Checks
    # ------------------------------------------------------

    check("3 Rows", len(df) == 3)

    check(
        "Columns",
        list(df.columns) == expected_columns
    )

    # ------------------------------------------------------
    # Datetime
    # ------------------------------------------------------

    check(
        "Datetime Type",
        pd.api.types.is_datetime64_any_dtype(
            df["datetime"]
        )
    )

    # ------------------------------------------------------
    # Sorted
    # ------------------------------------------------------

    check(
        "Sorted",
        df["datetime"].is_monotonic_increasing
    )

    # ------------------------------------------------------
    # Numeric Columns
    # ------------------------------------------------------

    for col in [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]:

        check(
            f"{col} Numeric",
            pd.api.types.is_numeric_dtype(df[col])
        )

    # ------------------------------------------------------
    # Values
    # ------------------------------------------------------

    first = df.iloc[0]

    check("Open", first["open"] == 25240.0)
    check("High", first["high"] == 25265.0)
    check("Low", first["low"] == 25230.0)
    check("Close", first["close"] == 25260.0)
    check("Volume", first["volume"] == 1500.0)

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