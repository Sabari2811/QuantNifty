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

from engine.live_greeks_engine import LiveGreeksEngine


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
    print("Live Greeks Engine Test")
    print("=" * 70)

    engine = LiveGreeksEngine()

    # ------------------------------------------------------
    # Mock Option Chain
    # ------------------------------------------------------

    option_chain = pd.DataFrame(
        [
            {
                "Strike": 25000,
                "CE_ID": 111,
                "CE_LTP": 150,
                "CE_OI": 45000,
                "CE_VOLUME": 1200,

                "PE_ID": 222,
                "PE_LTP": 140,
                "PE_OI": 43000,
                "PE_VOLUME": 900,
            },
            {
                "Strike": 25100,
                "CE_ID": 333,
                "CE_LTP": 120,
                "CE_OI": 39000,
                "CE_VOLUME": 950,

                "PE_ID": 444,
                "PE_LTP": 165,
                "PE_OI": 47000,
                "PE_VOLUME": 1300,
            }
        ]
    )

    # ------------------------------------------------------
    # Calculate Greeks
    # ------------------------------------------------------

    df = engine.calculate_chain_greeks(
        option_chain=option_chain,
        spot_price=25050,
        expiry="31/12/2026 15:30"
    )

    print(df)

    # ------------------------------------------------------
    # Row Count
    # ------------------------------------------------------

    check("Row Count", len(df) == len(option_chain))

    # ------------------------------------------------------
    # Expected Greek Columns
    # ------------------------------------------------------

    greek_columns = [

        "CE_IV",
        "CE_DELTA",
        "CE_GAMMA",
        "CE_THETA",
        "CE_VEGA",
        "CE_RHO",

        "PE_IV",
        "PE_DELTA",
        "PE_GAMMA",
        "PE_THETA",
        "PE_VEGA",
        "PE_RHO"

    ]

    for col in greek_columns:

        check(f"{col} exists", col in df.columns)

    # ------------------------------------------------------
    # Original Columns Preserved
    # ------------------------------------------------------

    original_columns = [

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

    for col in original_columns:

        check(f"{col} preserved", col in df.columns)

    # ------------------------------------------------------
    # At least one valid CE calculation
    # ------------------------------------------------------

    ce_valid = df["CE_IV"].notna().sum()

    print("\nValid CE Greeks :", ce_valid)

    # ------------------------------------------------------
    # At least one valid PE calculation
    # ------------------------------------------------------

    pe_valid = df["PE_IV"].notna().sum()

    print("Valid PE Greeks :", pe_valid)

    check(
        "At least one CE or PE solved",
        (ce_valid + pe_valid) > 0
    )

    # ------------------------------------------------------
    # Numeric values where available
    # ------------------------------------------------------

    for col in greek_columns:

        valid = df[col].dropna()

        if len(valid) > 0:

            check(
                f"{col} numeric",
                pd.api.types.is_numeric_dtype(valid)
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