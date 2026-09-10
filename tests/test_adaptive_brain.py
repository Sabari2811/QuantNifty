from types import SimpleNamespace

from analytics.intelligence.models import TradeIntelligenceRecord
from brain.adaptive_brain import AdaptiveBrain, BrainStore


class FakeExtractor:
    def extract(self, ctx):
        return TradeIntelligenceRecord(signal="BUY", option_type="CE", confidence=80.0)


def test_brain_persists_unresolved_observation_without_learning(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    result = brain.observe(SimpleNamespace(cycle_no=1), broker=None)

    assert result.status == "WAITING_OUTCOME"
    assert result.outcome == ""
    assert result.persisted is True
    assert brain.store.count() == 1


def test_brain_learns_only_from_resolved_outcome(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    trade = SimpleNamespace(closed=True, pnl=125.0)
    broker = SimpleNamespace(last_trade=trade)

    result = brain.observe(SimpleNamespace(cycle_no=2), broker=broker)

    assert result.status == "LEARNED"
    assert result.outcome == "WIN"
    assert result.historical_win_rate == 0.0
    assert brain.store.count() == 1


def test_brain_learning_uses_previous_resolved_history(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    winning = SimpleNamespace(closed=True, pnl=100.0)
    broker = SimpleNamespace(last_trade=winning)

    first = brain.observe(SimpleNamespace(cycle_no=1), broker=broker)
    second = brain.observe(SimpleNamespace(cycle_no=2), broker=broker)

    assert first.historical_win_rate == 0.0
    assert second.historical_win_rate == 100.0
    assert brain.store.count() == 2


def test_brain_deduplicates_resolved_trade_by_order_id(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    order = SimpleNamespace(order_id="PAPER-001")
    trade = SimpleNamespace(order=order, closed=True, pnl=100.0)
    broker = SimpleNamespace(last_trade=trade)

    first = brain.observe(SimpleNamespace(cycle_no=1), broker=broker)
    second = brain.observe(SimpleNamespace(cycle_no=2), broker=broker)

    assert first.status == "LEARNED"
    assert first.outcome == "WIN"
    assert second.status == "ALREADY_LEARNED"
    assert second.outcome == ""
    assert brain.store.count() == 2
    learned = [r for r in brain.memory.records if r.outcome == "WIN"]
    assert len(learned) == 1


def test_brain_restores_resolved_history_after_restart(tmp_path):
    path = tmp_path / "brain.jsonl"
    first_brain = AdaptiveBrain(BrainStore(path))
    first_brain.extractor = FakeExtractor()
    first_brain.observe(
        SimpleNamespace(cycle_no=1),
        broker=SimpleNamespace(last_trade=SimpleNamespace(closed=True, pnl=100.0)),
    )

    restarted = AdaptiveBrain(BrainStore(path))
    restarted.extractor = FakeExtractor()
    result = restarted.observe(SimpleNamespace(cycle_no=2), broker=None)

    assert result.status == "WAITING_OUTCOME"
    assert result.historical_win_rate == 100.0
    assert restarted.memory.size == 2


def test_brain_sql_store_restores_history_after_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'brain.db'}"
    first_brain = AdaptiveBrain(BrainStore(database_url=url))
    first_brain.extractor = FakeExtractor()
    first_brain.observe(
        SimpleNamespace(cycle_no=1),
        broker=SimpleNamespace(last_trade=SimpleNamespace(closed=True, pnl=100.0)),
    )
    first_brain.store.close()

    restarted = AdaptiveBrain(BrainStore(database_url=url))
    restarted.extractor = FakeExtractor()
    result = restarted.observe(SimpleNamespace(cycle_no=2), broker=None)

    assert result.historical_win_rate == 100.0
    assert restarted.memory.size == 2
    restarted.store.close()
