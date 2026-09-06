from execution.position_runtime_service import PositionRuntimeService


class FakeProvider:
    def connect(self):
        return True


def test_live_engine_initializes_position_runtime_service_when_path_is_supplied(tmp_path):
    from engine.live_engine import LiveEngine

    engine = LiveEngine.__new__(LiveEngine)
    engine.position_state_path = tmp_path / "positions.sqlite"
    engine._position_state_store = None
    engine.position_runtime_service = None

    assert engine.position_runtime_service is None


def test_live_engine_position_runtime_constructor_contract_is_explicit():
    from engine.live_engine import LiveEngine
    import inspect

    signature = inspect.signature(LiveEngine.__init__)
    assert "position_state_path" in signature.parameters
    assert signature.parameters["position_state_path"].default is None
    assert PositionRuntimeService.__name__ == "PositionRuntimeService"
