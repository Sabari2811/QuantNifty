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

from engine.state_manager import StateManager


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
    print("State Manager Test")
    print("=" * 70)

    manager = StateManager()

    # ------------------------------------------------------
    # Initial State
    # ------------------------------------------------------

    print("\n[1] Initial State")

    check(
        "Previous Snapshot is None",
        manager.get_previous_snapshot() is None
    )

    # ------------------------------------------------------
    # First Update
    # ------------------------------------------------------

    print("\n[2] Update Snapshot")

    snapshot1 = {

        "Spot": 25050,
        "PCR": 0.92,
        "Bias": "Sideways"

    }

    manager.update_snapshot(snapshot1)

    check(
        "Snapshot Stored",
        manager.get_previous_snapshot() == snapshot1
    )

    # ------------------------------------------------------
    # Second Update
    # ------------------------------------------------------

    print("\n[3] Overwrite Snapshot")

    snapshot2 = {

        "Spot": 25100,
        "PCR": 1.18,
        "Bias": "Bullish"

    }

    manager.update_snapshot(snapshot2)

    check(
        "Snapshot Updated",
        manager.get_previous_snapshot() == snapshot2
    )

    # ------------------------------------------------------
    # Clear
    # ------------------------------------------------------

    print("\n[4] Clear Snapshot")

    manager.clear()

    check(
        "Snapshot Cleared",
        manager.get_previous_snapshot() is None
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