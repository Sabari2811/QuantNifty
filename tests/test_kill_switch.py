import pytest

from execution.kill_switch import KillSwitch


def test_kill_switch_is_inactive_by_default():
    switch = KillSwitch()

    allowed, reason = switch.check()

    assert allowed is True
    assert reason == "Kill switch is inactive."


def test_activation_blocks_execution_and_preserves_reason():
    switch = KillSwitch()
    switch.activate("Emergency stop: provider state uncertain")

    allowed, reason = switch.check()

    assert allowed is False
    assert reason == "Emergency stop: provider state uncertain"


def test_activation_requires_non_empty_reason():
    with pytest.raises(ValueError, match="activation reason is required"):
        KillSwitch().activate("   ")


def test_deactivation_clears_block_and_reason():
    switch = KillSwitch()
    switch.activate("manual halt")
    switch.deactivate()

    allowed, reason = switch.check()

    assert allowed is True
    assert reason == "Kill switch is inactive."
