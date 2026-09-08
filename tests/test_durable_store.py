from monitoring.durable_store import SqlAppendStore


def test_sql_append_store_persists_and_restores(tmp_path):
    path = tmp_path / "runtime.db"
    url = f"sqlite:///{path}"

    first = SqlAppendStore(url, "events")
    first.append({"cycle_no": 1, "state": "READY"})
    first.append({"cycle_no": 2, "state": "BLOCKED"})
    assert first.count() == 2
    first.close()

    restarted = SqlAppendStore(url, "events")
    assert restarted.records() == [
        {"cycle_no": 1, "state": "READY"},
        {"cycle_no": 2, "state": "BLOCKED"},
    ]
    restarted.close()


def test_sql_append_store_is_append_only(tmp_path):
    store = SqlAppendStore(f"sqlite:///{tmp_path / 'runtime.db'}", "events")
    store.append({"event": "A"})
    store.append({"event": "A"})
    assert store.count() == 2
    assert store.records() == [{"event": "A"}, {"event": "A"}]
    store.close()
