import os
import sys
import traceback
from unittest.mock import MagicMock, patch

# ----------------------------------------------------------
# Add Project Root
# ----------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.session_manager import SessionManager


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
# Successful Login
# ----------------------------------------------------------

def test_success():

    print("\n[1] Successful Login")

    with patch("engine.session_manager.BreezeConnect") as MockBreeze:

        mock_breeze = MagicMock()
        MockBreeze.return_value = mock_breeze

        manager = SessionManager()

        result = manager.connect()

        mock_breeze.generate_session.assert_called_once()

        check(
            "Returned Breeze Instance",
            result == mock_breeze
        )

        print("✓ generate_session called")


# ----------------------------------------------------------
# Failed Login
# ----------------------------------------------------------

def test_failure():

    print("\n[2] Failed Login")

    with patch("engine.session_manager.BreezeConnect") as MockBreeze:

        mock_breeze = MagicMock()

        mock_breeze.generate_session.side_effect = Exception(
            "Invalid Session"
        )

        MockBreeze.return_value = mock_breeze

        manager = SessionManager()

        try:

            manager.connect()

            raise Exception("Expected Exception")

        except Exception:

            print("✓ Exception propagated")


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def run():

    print("=" * 70)
    print("Session Manager Test")
    print("=" * 70)

    test_success()

    test_failure()

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