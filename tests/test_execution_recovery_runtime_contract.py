from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

from execution.execution_audit_store import ExecutionAuditRecord
from execution.execution_contract import ExecutionAction, ExecutionStatus, OrderIntent
from execution.execution_recovery import evaluate_recovery, recover_pending


def build_record(status: str) -> ExecutionAuditRecord:
    now = datetime.now()
    intent = OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=f"qn-recovery-runtime-{status.lower()}",
    )
    return ExecutionAuditRecord(
        client_order_id=intent.client_order_id,
        symbol=intent.symbol,
        option_type=intent.option_type,
        strike=intent.strike,
        quantity=intent.quantity,
        action=intent.action.value,
        limit_price=intent.limit_price,
        strategy_name=intent.strategy_name,
        source=intent.source,
        broker_order_id="ORD-1",
        status=status,
        filled_quantity=0,
        average_fill_price=None,
        reason="",
        intent_created_at=now,
        result_timestamp=now,
    )


def test_ambiguous_persisted_result_requires_reconciliation():
    decision = evaluate_recovery(build_record("UNKNOWN"))

    assert not decision.safe_to_continue
    assert decision.requires_reconciliation
    assert not decision.requires_manual_resolution


def test_submitted_persisted_result_requires_reconciliation():
    decision = evaluate_recovery(build_record("SUBMITTED"))

    assert not decision.safe_to_continue
    assert decision.requires_reconciliation


def test_executed_persisted_result_is_safe_to_continue():
    decision = evaluate_recovery(build_record("EXECUTED"))

    assert decision.safe_to_continue
    assert not decision.requires_reconciliation
    assert not decision.requires_manual_resolution


def test_recover_pending_uses_store_pending_contract():
    record = build_record("UNKNOWN")

    class FakeStore:
        def load_pending(self):
            return (record,)

    pending = recover_pending(FakeStore())

    assert pending == (record,)
    assert pending[0].status == "UNKNOWN"
