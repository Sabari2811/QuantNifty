from types import SimpleNamespace

from analytics.intelligence.models import TradeIntelligenceRecord
from brain.adaptive_brain import AdaptiveBrain, BrainStore


class FakeExtractor:
    def extract(self, ctx):
        return TradeIntelligenceRecord(signal="BUY_CALL", option_type="CE", confidence=80.0)


def _position(order_id="PAPER-001"):
    return SimpleNamespace(order=SimpleNamespace(order_id=order_id), closed=False, pnl=0.0)


def _closed(order_id="PAPER-001", pnl=100.0):
    return SimpleNamespace(order=SimpleNamespace(order_id=order_id, order_time=SimpleNamespace()), closed=True, pnl=pnl, exit_price=110.0, exit_time=None)


def test_brain_persists_unresolved_observation_without_learning(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    result = brain.observe(SimpleNamespace(cycle_no=1), broker=None)
    assert result.status == "WAITING_OUTCOME"
    assert result.outcome == ""
    assert result.persisted is True
    assert brain.store.count() == 1
    assert brain.memory.size == 0


def test_brain_learns_from_the_exact_entry_fingerprint(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    first = brain.observe(SimpleNamespace(cycle_no=1), broker=SimpleNamespace(position=_position("PAPER-001"), last_trade=None))
    assert first.status == "WAITING_OUTCOME"
    second = brain.observe(SimpleNamespace(cycle_no=2), broker=SimpleNamespace(position=None, last_trade=_closed("PAPER-001", 125.0)))
    assert second.status == "LEARNED"
    assert second.outcome == "WIN"
    assert second.trade_id == "PAPER-001"
    assert brain.store.count() == 2
    assert brain.memory.size == 1
    assert brain.memory.records[0].outcome == "WIN"


def test_brain_deduplicates_resolved_trade_by_order_id(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    brain.observe(SimpleNamespace(cycle_no=1), broker=SimpleNamespace(position=_position("PAPER-001"), last_trade=None))
    first = brain.observe(SimpleNamespace(cycle_no=2), broker=SimpleNamespace(position=None, last_trade=_closed("PAPER-001", 100.0)))
    second = brain.observe(SimpleNamespace(cycle_no=3), broker=SimpleNamespace(position=None, last_trade=_closed("PAPER-001", 100.0)))
    assert first.status == "LEARNED"
    assert second.status == "ALREADY_LEARNED"
    assert second.trade_id == "PAPER-001"
    assert len([r for r in brain.memory.records if r.outcome == "WIN"]) == 1


def test_brain_vetoes_repeated_unprofitable_pattern(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    for _ in range(8):
        brain.memory.add(TradeIntelligenceRecord(signal="BUY_CALL", option_type="CE", confidence=80.0, pnl=-100.0, outcome="LOSS"))
    result = brain.evaluate(SimpleNamespace())
    assert result.gate == "BLOCK"
    assert result.status == "VETO"
    assert result.sample_count == 8
    assert result.matching_losses == 8
    assert result.historical_win_rate == 0.0


def test_brain_allows_repeated_profitable_pattern(tmp_path):
    brain = AdaptiveBrain(BrainStore(tmp_path / "brain.jsonl"))
    brain.extractor = FakeExtractor()
    for _ in range(8):
        brain.memory.add(TradeIntelligenceRecord(signal="BUY_CALL", option_type="CE", confidence=80.0, pnl=100.0, outcome="WIN"))
    result = brain.evaluate(SimpleNamespace())
    assert result.gate == "ALLOW"
    assert result.status == "PASS"
    assert result.sample_count == 8
    assert result.matching_wins == 8
    assert result.historical_win_rate == 100.0


def test_brain_restores_only_resolved_history_after_restart(tmp_path):
    path = tmp_path / "brain.jsonl"
    first_brain = AdaptiveBrain(BrainStore(path))
    first_brain.extractor = FakeExtractor()
    first_brain.observe(SimpleNamespace(cycle_no=1), broker=SimpleNamespace(position=_position("PAPER-001"), last_trade=None))
    first_brain.observe(SimpleNamespace(cycle_no=2), broker=SimpleNamespace(position=None, last_trade=_closed("PAPER-001", 100.0)))
    restarted = AdaptiveBrain(BrainStore(path))
    assert restarted.memory.size == 1
    assert restarted.memory.records[0].outcome == "WIN"


def test_brain_sql_store_restores_resolved_history_after_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'brain.db'}"
    first_brain = AdaptiveBrain(BrainStore(database_url=url))
    first_brain.extractor = FakeExtractor()
    first_brain.observe(SimpleNamespace(cycle_no=1), broker=SimpleNamespace(position=_position("PAPER-001"), last_trade=None))
    first_brain.observe(SimpleNamespace(cycle_no=2), broker=SimpleNamespace(position=None, last_trade=_closed("PAPER-001", 100.0)))
    first_brain.store.close()
    restarted = AdaptiveBrain(BrainStore(database_url=url))
    assert restarted.memory.size == 1
    restarted.store.close()
