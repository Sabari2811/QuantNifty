import os
import sys
import traceback
import io
from contextlib import redirect_stdout

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.terminal_dashboard import TerminalDashboard


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
    print("Terminal Dashboard Test")
    print("=" * 70)

    dashboard = TerminalDashboard()

    analytics = {

        "decision": {
            "signal": "BUY CE",
            "confidence": 82
        },

        "probability": {
            "up": 68,
            "down": 32
        },

        "dealer": {
            "gamma": "Positive",
            "delta": "Long"
        },

        "market_regime": {
            "trend": "Bullish"
        }

    }

    buffer = io.StringIO()

    with redirect_stdout(buffer):

        dashboard.show(analytics)

    output = buffer.getvalue()

    print(output)

    # ------------------------------------------------------
    # Validate Output
    # ------------------------------------------------------

    check(
        "Header",
        "QUANTNIFTY LIVE" in output
    )

    check(
        "Decision Section",
        "Decision" in output
    )

    check(
        "Probability Section",
        "Probability" in output
    )

    check(
        "Dealer Section",
        "Dealer" in output
    )

    check(
        "Regime Section",
        "Regime" in output
    )

    check(
        "BUY CE",
        "BUY CE" in output
    )

    check(
        "Bullish",
        "Bullish" in output
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