from types import SimpleNamespace

from execution.execution_audit_store import SQLiteExecutionAuditStore
from engine.live_engine import LiveEngine


class FakeProvider:
    def connect(self):
        return None


class FakePipeline:
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.audit_store = None
        self.executed = False

    def execute(self, ctx):
        self.executed = True

    def sync_context(self, ctx):
        return None


class FakeRiskManager:
    state = "TEST"


def test_live_engine_can_inject_durable_audit_store(tmp_path):
    store = SQLiteExecutionAuditStore(tmp_path / "execution_audit.db")
    pipeline = FakePipeline(FakeRiskManager())
    pipeline.audit_store = store

    engine = LiveEngine(
        provider=FakeProvider(),
        paper_broker=SimpleNamespace(),
        trade_pipeline=pipeline,
    )

    assert engine.trade_pipeline is pipeline
    assert engine.trade_pipeline.audit_store is store
    assert engine.risk_manager is pipeline.risk_manager
    store.close()
