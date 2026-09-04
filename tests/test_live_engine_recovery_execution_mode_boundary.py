from __future__ import annotations

from types import SimpleNamespace

from execution.execution_mode import ExecutionMode


def test_live_engine_recovery_boundary_keeps_execution_mode_explicit():
    recovery_state = SimpleNamespace(
        mode=ExecutionMode.PAPER,
        safe_to_continue=False,
        requires_reconciliation=True,
    )

    assert recovery_state.mode is ExecutionMode.PAPER
    assert recovery_state.safe_to_continue is False
    assert recovery_state.requires_reconciliation is True
