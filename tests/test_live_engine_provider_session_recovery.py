from __future__ import annotations

from types import SimpleNamespace

from execution.execution_audit_store import InMemoryExecutionAuditStore
from execution.execution_contract import ExecutionAction, ExecutionResult, ExecutionStatus, OrderIntent
from execution.execution_recovery import recover_pending


class FakeProvider:
    def __init__(self):
        self.connected = False
        self.connect_calls = 0
        self.disconnect_calls = 0

    def connect(self):
        self.connect_calls += 1
        self.connected = True
        return True

    def disconnect(self):
        self.disconnect_calls += 1
        self.connected = False


def build_intent(client_order_id: str) -> OrderIntent:
    return OrderIntent(
        symbol="NIFTY",
        option_type="CE",
        strike=25000,
        action=ExecutionAction.BUY,
        quantity=75,
        limit_price=120.0,
        client_order_id=client_order_id,
    )


def test_provider_session_can_reconnect_without_mutating_persisted_recovery_state():
    provider = FakeProvider()
    assert provider.connect() is True
    provider.disconnect()
    assert provider.connected is False
    assert provider.connect() is True
    assert provider.connect_calls == 2
    assert provider.disconnect_calls == 1


def test_reconnect_does_not_clear_pending_execution_audit_state():
    store = InMemoryExecutionAuditStore()
    intent = build_intent("provider-recovery-1")
    store.append(
        __import__("execution.execution_audit_store", fromlist=["ExecutionAuditRecord"])
        .ExecutionAuditRecord.from_result(
            ExecutionResult(status=ExecutionStatus.UNKNOWN, intent=intent)
        )
    )

    provider = FakeProvider()
    provider.connect()
    provider.disconnect()
    provider.connect()

    pending = recover_pending(store)
    assert len(pending) == 1
    assert pending[0].client_order_id == "provider-recovery-1"
    assert pending[0].status == "UNKNOWN"
