from datetime import datetime

from simulation.replay_state import ReplayState


def test_default_values():
    state = ReplayState()

    assert state.current_cycle == 0
    assert state.total_cycles == 0
    assert state.speed == 1
    assert state.is_playing is False
    assert state.paused is False
    assert state.finished is False
    assert state.current_timestamp is None


def test_progress():
    state = ReplayState(total_cycles=100)

    state.current_cycle = 25

    assert state.progress == 25.0


def test_progress_zero_cycles():
    state = ReplayState()

    assert state.progress == 0.0


def test_reset():
    state = ReplayState(
        current_cycle=80,
        total_cycles=100,
        speed=4,
        is_playing=True,
        paused=True,
        finished=True,
        current_timestamp=datetime.now(),
    )

    state.reset()

    assert state.current_cycle == 0
    assert state.speed == 1
    assert state.is_playing is False
    assert state.paused is False
    assert state.finished is False
    assert state.current_timestamp is None


def test_update():
    state = ReplayState(total_cycles=100)

    ts = datetime.now()

    state.update(cycle=10, timestamp=ts)

    assert state.current_cycle == 10
    assert state.current_timestamp == ts
    assert state.finished is False


def test_finished():
    state = ReplayState(total_cycles=100)

    state.update(cycle=100)

    assert state.finished is True