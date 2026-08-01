from datetime import datetime

from simulation.replay_controller import ReplayController
from simulation.replay_state import ReplayState


class DummySnapshot:

    def __init__(self):
        self.timestamp = datetime.now()


class DummySession:

    def __init__(self):
        self.index = 0
        self.total = 100

    def next(self):
        self.index += 1
        return DummySnapshot()

    def previous(self):
        self.index -= 1
        return DummySnapshot()

    def current(self):
        return DummySnapshot()

    def reset(self):
        self.index = 0


def test_play():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller.play()

    assert controller.state.is_playing
    assert not controller.state.paused


def test_pause():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller.pause()

    assert controller.state.paused


def test_stop():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller.play()

    controller.stop()

    assert controller.state.current_cycle == 0
    assert controller.state.is_playing is False


def test_speed():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller.set_speed(5)

    assert controller.state.speed == 5


def test_next():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller.next()

    assert controller.state.current_cycle == 1


def test_seek():

    controller = ReplayController(
        DummySession(),
        ReplayState(),
    )

    controller._session.seek = lambda index: DummySnapshot()
    controller._session.index = 25

    controller.seek(25)

    assert controller.state.current_cycle == 25