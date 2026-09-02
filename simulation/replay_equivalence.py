from __future__ import annotations

from dataclasses import asdict, is_dataclass
from math import isclose
from typing import Any

import pandas as pd


class ReplayEquivalence:
    """Result of comparing recorded and recomputed replay outputs."""

    def __init__(self, equivalent: bool, mismatches: tuple[str, ...] = ()):
        self.equivalent = equivalent
        self.mismatches = mismatches

    def as_dict(self) -> dict[str, Any]:
        return {
            "equivalent": self.equivalent,
            "mismatches": list(self.mismatches),
        }


def _normalize(value):
    if is_dataclass(value):
        return _normalize(asdict(value))
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def _compare(expected, actual, path: str, mismatches: list[str], tolerance: float):
    expected = _normalize(expected)
    actual = _normalize(actual)

    if isinstance(expected, dict) or isinstance(actual, dict):
        if not isinstance(expected, dict) or not isinstance(actual, dict):
            mismatches.append(path or "root")
            return
        for key in sorted(set(expected) | set(actual)):
            if key not in expected or key not in actual:
                mismatches.append(f"{path}.{key}" if path else key)
                continue
            _compare(expected[key], actual[key], f"{path}.{key}" if path else key, mismatches, tolerance)
        return

    if isinstance(expected, (list, tuple)) or isinstance(actual, (list, tuple)):
        if not isinstance(expected, (list, tuple)) or not isinstance(actual, (list, tuple)):
            mismatches.append(path or "root")
            return
        if len(expected) != len(actual):
            mismatches.append(path or "root")
            return
        for index, (left, right) in enumerate(zip(expected, actual)):
            _compare(left, right, f"{path}[{index}]", mismatches, tolerance)
        return

    if expected is None or actual is None:
        if expected is not actual:
            mismatches.append(path or "root")
        return

    if isinstance(expected, float) and isinstance(actual, (int, float)):
        if not isclose(expected, float(actual), rel_tol=tolerance, abs_tol=tolerance):
            mismatches.append(path or "root")
        return

    if isinstance(actual, float) and isinstance(expected, (int, float)):
        if not isclose(float(expected), actual, rel_tol=tolerance, abs_tol=tolerance):
            mismatches.append(path or "root")
        return

    if expected != actual:
        mismatches.append(path or "root")


def compare_replay_outputs(
    expected_decision,
    actual_decision,
    expected_intelligence,
    actual_intelligence,
    *,
    tolerance: float = 1e-9,
) -> ReplayEquivalence:
    """Compare canonical recorded outputs with replay-recomputed outputs.

    ``authoritative_signal`` is execution-mutation provenance captured on the
    recomputed Decision so the original signal survives downstream mutation.
    Older recorded snapshots predate that field, so its absence in the
    recorded artifact must not create replay drift. When both artifacts carry
    the field, it remains part of the equivalence comparison.
    """
    mismatches: list[str] = []

    expected_decision_normalized = _normalize(expected_decision)
    actual_decision_normalized = _normalize(actual_decision)
    if (
        isinstance(expected_decision_normalized, dict)
        and isinstance(actual_decision_normalized, dict)
        and "authoritative_signal" not in expected_decision_normalized
    ):
        actual_decision_normalized.pop("authoritative_signal", None)

    _compare(expected_decision_normalized, actual_decision_normalized, "decision", mismatches, tolerance)
    _compare(expected_intelligence, actual_intelligence, "intelligence", mismatches, tolerance)
    return ReplayEquivalence(not mismatches, tuple(mismatches))
