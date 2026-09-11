from types import SimpleNamespace

from brain.adaptive_brain import BrainDecision
from decision.models.decision import Decision
from decision.models.trade import Trade
from engine.live_engine import LiveEngine


class FakeBrain:
    def __init__(self, evidence):
        self.evidence = evidence

    def evaluate(self, ctx):
        return self.evidence


def _engine(signal="BUY_CALL", evidence=None):
    engine = LiveEngine.__new__(LiveEngine)
    engine.ctx = SimpleNamespace(
        decision=Decision(signal=SimpleNamespace(name=signal), trade=Trade(symbol="NIFTY"), score={}, reasons=[]),
        brain_decision=None,
    )
    engine.adaptive_brain = FakeBrain(evidence)
    return engine


def test_brain_veto_converts_trade_to_wait_without_reversing_direction():
    evidence = BrainDecision("VETO", "BUY_CALL", 91.0, 37.5, -120.0, 12, 4, 8, "BLOCK", "weak learned edge")
    engine = _engine(evidence=evidence)

    engine._apply_brain_gate()

    assert engine.ctx.decision.signal.name == "WAIT"
    assert engine.ctx.decision.authoritative_signal == "BUY_CALL"
    assert engine.ctx.decision.trade.symbol == "NIFTY"
    assert engine.ctx.decision.trade.contract is None
    assert engine.ctx.decision.validation.grade == "BRAIN_VETO"
    assert engine.ctx.brain_decision.gate == "BLOCK"


def test_brain_allow_preserves_canonical_direction():
    evidence = BrainDecision("PASS", "BUY_PUT", 88.0, 72.0, 145.0, 10, 8, 2, "ALLOW", "positive learned edge")
    engine = _engine(signal="BUY_PUT", evidence=evidence)

    engine._apply_brain_gate()

    assert engine.ctx.decision.signal.name == "BUY_PUT"
    assert engine.ctx.decision.authoritative_signal == ""
    assert engine.ctx.decision.score["brain_historical_win_rate"] == 72.0
    assert engine.ctx.decision.score["brain_gate"] == "ALLOW"
