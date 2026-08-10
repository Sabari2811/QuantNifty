import sys
import types
from unittest.mock import MagicMock, patch


# ----------------------------------------------------------
# Isolate the legacy Breeze SDK at test-import time.
#
# engine.session_manager imports:
#     from breeze_connect import BreezeConnect
#
# The real Breeze package performs SDK initialization during
# import and currently expects SECURITY_MASTER_URL.
#
# We only need to test SessionManager's behavior, so inject
# a lightweight fake module before importing it.
# ----------------------------------------------------------

fake_breeze_module = types.ModuleType("breeze_connect")


class FakeBreezeConnect:
    def __init__(self, *args, **kwargs):
        pass


fake_breeze_module.BreezeConnect = FakeBreezeConnect

sys.modules["breeze_connect"] = fake_breeze_module


from engine.session_manager import SessionManager


def test_session_manager_successful_login():

    with patch("engine.session_manager.BreezeConnect") as MockBreeze:

        mock_breeze = MagicMock()
        MockBreeze.return_value = mock_breeze

        manager = SessionManager()

        result = manager.connect()

        MockBreeze.assert_called_once()
        mock_breeze.generate_session.assert_called_once()

        assert result == mock_breeze


def test_session_manager_failed_login_propagates_exception():

    with patch("engine.session_manager.BreezeConnect") as MockBreeze:

        mock_breeze = MagicMock()

        mock_breeze.generate_session.side_effect = Exception(
            "Invalid Session"
        )

        MockBreeze.return_value = mock_breeze

        manager = SessionManager()

        try:
            manager.connect()
            assert False, "Expected SessionManager.connect() to raise"
        except Exception as exc:
            assert str(exc) == "Invalid Session"
