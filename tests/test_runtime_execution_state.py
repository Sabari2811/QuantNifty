from execution.execution_lifecycle import ExecutionLifecycleAction
from core.runtime_context import RuntimeContext


def test_runtime_context_exposes_canonical_execution_state_defaults():
    ctx = RuntimeContext()

    assert ctx.execution_intent is None
    assert ctx.execution_result is None
    assert ctx.execution_lifecycle == ""


def test_runtime_context_accepts_reconciliation_required_lifecycle_state():
    ctx = RuntimeContext()
    ctx.execution_lifecycle = ExecutionLifecycleAction.RECONCILE.value

    assert ctx.execution_lifecycle == "RECONCILE"


def test_runtime_context_lifecycle_is_distinct_from_trade_status():
    ctx = RuntimeContext()
    ctx.trade_status = "BLOCKED"
    ctx.execution_lifecycle = ExecutionLifecycleAction.RECONCILE.value

    assert ctx.trade_status == "BLOCKED"
    assert ctx.execution_lifecycle == "RECONCILE"
