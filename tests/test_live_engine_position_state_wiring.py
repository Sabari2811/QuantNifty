from types import SimpleNamespace

from execution.position_runtime_service import PositionRuntimeService


class FakeStore:
    def __init__(self):
        self.saved = []

    def save(self, state):
        self.saved.append(state)
        return state


def test_live_engine_exposes_position_runtime_service():
    from engine.live_engine import LiveEngine

    engine = object.__new__(LiveEngine)
    engine.position_runtime_service = PositionRuntimeService(FakeStore())

    assert isinstance(engine.position_runtime_service, PositionRuntimeService)


def test_runtime_service_can_be_injected_without_touching_execution_pipeline():
    from engine.live_engine import LiveEngine

    engine = object.__new__(LiveEngine)
    service = PositionRuntimeService(FakeStore())
    engine.position_runtime_service = service
    engine.trade_pipeline = SimpleNamespace()

    assert engine.position_runtime_service is service
    assert engine.trade_pipeline is not service
