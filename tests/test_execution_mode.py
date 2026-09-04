from execution.execution_mode import ExecutionMode


def test_execution_mode_values_are_explicit():
    assert ExecutionMode.PAPER.value == "PAPER"
    assert ExecutionMode.LIVE.value == "LIVE"


def test_execution_mode_is_str_enum():
    assert isinstance(ExecutionMode.PAPER, str)
    assert isinstance(ExecutionMode.LIVE, str)
