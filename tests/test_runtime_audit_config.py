from execution.execution_audit_store import SQLiteExecutionAuditStore
from execution.runtime_audit_config import build_runtime_audit_store


def test_runtime_audit_factory_returns_sqlite_store(tmp_path):
    path = tmp_path / "runtime" / "execution_audit.db"

    store = build_runtime_audit_store(path)

    assert isinstance(store, SQLiteExecutionAuditStore)
    assert store.path == str(path)
    assert path.exists()
    store.close()
