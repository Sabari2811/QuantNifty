from types import SimpleNamespace

from engine.live_engine import LiveEngine
from execution.execution_audit_store import SQLiteExecutionAuditStore


class FakeProvider:
    def connect(self):
        return None


class FakeRiskManager:
    state = "TEST"


class FakeBroker:
    portfolio_engine = SimpleNamespace(portfolio=SimpleNamespace())


def test_live_engine_constructs_durable_audit_store_when_path_is_supplied(tmp_path):
    path = tmp_path / "runtime" / "execution_audit.db"

    engine = LiveEngine(
        provider=FakeProvider(),
        paper_broker=FakeBroker(),
        audit_store_path=path,
    )

    assert isinstance(engine.trade_pipeline.audit_store, SQLiteExecutionAuditStore)
    assert engine.trade_pipeline.audit_store.path == str(path)
    assert path.exists()
    engine.trade_pipeline.audit_store.close()


def test_live_engine_preserves_injected_trade_pipeline(tmp_path):
    class FakePipeline:
        def __init__(self):
            self.risk_manager = FakeRiskManager()
            self.audit_store = "injected"

        def execute(self, ctx):
            return None

        def sync_context(self, ctx):
            return None

    pipeline = FakePipeline()
    path = tmp_path / "should-not-be-created.db"

    engine = LiveEngine(
        provider=FakeProvider(),
        paper_broker=FakeBroker(),
        trade_pipeline=pipeline,
        audit_store_path=path,
    )

    assert engine.trade_pipeline is pipeline
    assert engine.trade_pipeline.audit_store == "injected"
    assert not path.exists()
