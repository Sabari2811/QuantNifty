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

from engine.oi_analyzer import OIAnalyzer


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
    print("OI Analyzer Test")
    print("=" * 70)

    analyzer = OIAnalyzer()

    option_chain = pd.DataFrame([

        {
            "Strike": 24900,
            "CE_OI": 100000,
            "PE_OI": 50000
        },

        {
            "Strike": 25000,
            "CE_OI": 150000,
            "PE_OI": 200000
        },

        {
            "Strike": 25100,
            "CE_OI": 120000,
            "PE_OI": 100000
        }

    ])

    result = analyzer.analyze(option_chain)

    print(result)

    # ------------------------------------------------------
    # Keys
    # ------------------------------------------------------

    expected_keys = [

        "Total Call OI",
        "Total Put OI",
        "PCR",
        "Support",
        "Resistance",
        "Max Put OI",
        "Max Call OI",
        "Market Bias"

    ]

    for key in expected_keys:

        check(f"{key} exists", key in result)

    # ------------------------------------------------------
    # Totals
    # ------------------------------------------------------

    check(
        "Total Call OI",
        result["Total Call OI"] == 370000
    )

    check(
        "Total Put OI",
        result["Total Put OI"] == 350000
    )

    # ------------------------------------------------------
    # PCR
    # ------------------------------------------------------

    expected_pcr = round(350000 / 370000, 2)

    check(
        "PCR",
        result["PCR"] == expected_pcr
    )

    # ------------------------------------------------------
    # Support / Resistance
    # ------------------------------------------------------

    check(
        "Support",
        result["Support"] == 25000
    )

    check(
        "Resistance",
        result["Resistance"] == 25000
    )

    # ------------------------------------------------------
    # Max OI
    # ------------------------------------------------------

    check(
        "Max Put OI",
        result["Max Put OI"] == 200000
    )

    check(
        "Max Call OI",
        result["Max Call OI"] == 150000
    )

    # ------------------------------------------------------
    # Bias
    # ------------------------------------------------------

    check(
        "Market Bias",
        result["Market Bias"] == "Sideways"
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