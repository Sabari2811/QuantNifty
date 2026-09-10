from types import SimpleNamespace

from engine.live_engine import LiveEngine
from risk.risk_manager import RiskManager


def test_risk_snapshot_exposes_policy_and_runtime_state():
    manager = RiskManager()
    portfolio = SimpleNamespace(
        capital=500000.0,
        invested_amount=50000.0,
        open_positions=[object()],
    )
    broker = SimpleNamespace(portfolio_engine=SimpleNamespace(portfolio=portfolio))

    snapshot = manager.snapshot(broker)

    assert snapshot["capital_per_trade"] == 100000
    assert snapshot["capital_utilization"] == 0.1
    assert snapshot["capital_utilization_limit"] == 0.40
    assert snapshot["max_daily_loss"] == -5000
    assert snapshot["max_trades_per_day"] == 10
    assert snapshot["max_open_positions"] == 1
    assert snapshot["cooldown"] == "NONE"
    assert snapshot["loss_limit"] == 3
    assert snapshot["open_positions"] == 1
    assert snapshot["trades_today"] == 0


def test_live_engine_persists_current_brain_observation():
    class FakeBrain:
        def observe(self, ctx, broker=None):
            return SimpleNamespace(
                status="WAITING_OUTCOME",
                cycle_no=ctx.cycle_no,
                signal="WAIT",
                outcome="",
                persisted=True,
            )

    engine = LiveEngine.__new__(LiveEngine)
    engine.ctx = SimpleNamespace(
        decision=SimpleNamespace(),
        market_context=SimpleNamespace(),
        cycle_no=12,
        brain_observation=None,
    )
    engine.provider = object()
    engine.paper_broker = object()
    engine.adaptive_brain = FakeBrain()

    observation = engine._observe_brain()

    assert observation.persisted is True
    assert observation.cycle_no == 12
    assert engine.ctx.brain_observation is observation
