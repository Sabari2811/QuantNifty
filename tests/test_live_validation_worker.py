from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import dashboard.live_validation_worker as worker
from dashboard.live_validation_worker import _health_snapshot, get_validation_interval_seconds, is_nse_derivatives_session_open


IST = ZoneInfo("Asia/Kolkata")


def test_live_validation_session_window():
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 15, tzinfo=IST))
    assert is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 9, 14, 59, tzinfo=IST))
    assert not is_nse_derivatives_session_open(datetime(2026, 9, 7, 15, 40, 1, tzinfo=IST))


def test_live_validation_skips_weekends():
    saturday = datetime(2026, 9, 12, 10, 0, tzinfo=IST)
    assert not is_nse_derivatives_session_open(saturday)


def test_live_validation_interval_is_fail_safe(monkeypatch):
    monkeypatch.delenv("LIVE_VALIDATION_INTERVAL_SECONDS", raising=False)
    assert get_validation_interval_seconds() == 60
    assert get_validation_interval_seconds("invalid") == 60
    assert get_validation_interval_seconds("2") == 5
    assert get_validation_interval_seconds("15") == 15


def test_live_validation_health_state_is_safe_metadata_only():
    snapshot = _health_snapshot()
    assert snapshot["status"] == "starting"
    assert snapshot["cycles"] == 0
    assert "token" not in snapshot
    assert "APITOKEN" not in snapshot


def test_initialize_runtime_injects_one_canonical_brain(monkeypatch):
    evidence_store = object()
    brain = SimpleNamespace(store=SimpleNamespace())
    provider = object()
    captured = {}

    class FakeEngine:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(worker, "create_live_evidence_store", lambda: evidence_store)
    monkeypatch.setattr(worker, "AdaptiveBrain", lambda: brain)
    monkeypatch.setattr(worker, "INDMoneyProvider", lambda: provider)
    monkeypatch.setattr(worker, "LiveEngine", FakeEngine)

    result = worker._initialize_runtime()

    assert result == (evidence_store, brain, provider, captured and captured)
    assert captured["provider"] is provider
    assert captured["adaptive_brain"] is brain


def test_run_validation_cycle_does_not_observe_brain_twice(monkeypatch):
    class FakeBrain:
        def __init__(self):
            self.observe_calls = 0
            self.store = SimpleNamespace(_sql_store=None)

        def observe(self, *args, **kwargs):
            self.observe_calls += 1
            raise AssertionError("worker must not call Brain.observe")

    class FakeEvidenceStore:
        durable = False

        def __init__(self):
            self.items = []

        def append(self, evidence):
            self.items.append(evidence)

    brain = FakeBrain()
    evidence_store = FakeEvidenceStore()
    observation = SimpleNamespace(status="WAITING_OUTCOME")
    ctx = SimpleNamespace(brain_observation=observation)

    class FakeEngine:
        def run_cycle(self):
            return ctx

    class FakeProvider:
        provider_name = "TEST"

    captured = {}

    def fake_build(ctx_arg, **kwargs):
        captured.update(kwargs)
        return SimpleNamespace(**kwargs, evidence_state="RECORDED")

    monkeypatch.setattr(worker, "build_live_cycle_evidence", fake_build)

    returned_ctx, evidence = worker.run_validation_cycle(
        evidence_store,
        brain,
        FakeProvider(),
        FakeEngine(),
    )

    assert returned_ctx is ctx
    assert evidence_store.items == [evidence]
    assert brain.observe_calls == 0
    assert ctx.brain_status == "WAITING_OUTCOME"
    assert ctx.learning_status == "PENDING_OUTCOME"
    assert captured["brain_status"] == "WAITING_OUTCOME"
    assert captured["learning_status"] == "PENDING_OUTCOME"
