from __future__ import annotations

from types import SimpleNamespace

from engine.live_engine import LiveEngine
from execution.execution_audit_store import SQLiteExecutionAuditStore


class FakeProvider:
    def connect(self):
        return None


class FakeTradePipeline:
    def __init__(self):
        self.risk_manager = SimpleNamespace()
        self.audit_store = SQLiteExecutionAuditStore(":memory:")


def test_live_engine_preserves_injected_pipeline_for_recovery_state():
    pipeline = FakeTradePipeline()
    engine = LiveEngine(provider=FakeProvider(), trade_pipeline=pipeline)

    assert engine.trade_pipeline is pipeline
    assert engine.risk_manager is pipeline.risk_manager


def test_live_engine_can_receive_persistent_audit_store_path_without_replacing_pipeline_contract(tmp_path):
    path = tmp_path / "execution_audit.sqlite"
    engine = LiveEngine(provider=FakeProvider(), audit_store_path=path)

    assert engine.trade_pipeline.audit_store is engine._runtime_audit_store
    assert isinstance(engine.trade_pipeline.audit_store, SQLiteExecutionAuditStore)
