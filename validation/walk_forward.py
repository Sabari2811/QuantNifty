"""Deterministic walk-forward and out-of-sample split utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence


@dataclass(frozen=True)
class WalkForwardWindow:
    index: int
    train: tuple[Any, ...]
    test: tuple[Any, ...]


def walk_forward_windows(
    records: Sequence[Any] | Iterable[Any],
    *,
    train_size: int,
    test_size: int,
    step: int | None = None,
) -> tuple[WalkForwardWindow, ...]:
    """Create ordered train/test windows without shuffling or overlap leakage.

    Records must already be in chronological order. The function never sorts
    them because silently sorting an unordered source could hide a data-quality
    problem.
    """
    if train_size < 1 or test_size < 1:
        raise ValueError("train_size and test_size must be >= 1")
    step = test_size if step is None else step
    if step < 1:
        raise ValueError("step must be >= 1")
    rows = tuple(records)
    windows: list[WalkForwardWindow] = []
    start = 0
    index = 1
    while start + train_size + test_size <= len(rows):
        train_end = start + train_size
        test_end = train_end + test_size
        windows.append(WalkForwardWindow(index, rows[start:train_end], rows[train_end:test_end]))
        start += step
        index += 1
    return tuple(windows)


def validate_temporal_order(records: Sequence[Any] | Iterable[Any], *, field: str = "timestamp") -> tuple[bool, tuple[str, ...]]:
    """Verify non-decreasing timestamps; malformed/missing timestamps fail closed."""
    rows = tuple(records)
    reasons: list[str] = []
    previous = None
    for index, row in enumerate(rows, start=1):
        value = row.get(field) if isinstance(row, dict) else getattr(row, field, None)
        if value is None:
            reasons.append(f"row_{index}:missing_{field}")
            continue
        if previous is not None and str(value) < str(previous):
            reasons.append(f"row_{index}:timestamp_out_of_order")
        previous = value
    return not reasons, tuple(reasons)
