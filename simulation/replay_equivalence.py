from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from math import isclose
from types import SimpleNamespace
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
    if isinstance(value, SimpleNamespace):
        return _normalize(vars(value))
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


def _recorded_json_projection(value):
    """Mirror SnapshotRecorder JSON conversion for replay parity checks.

    Recorded analytics are JSON artifacts. DataFrames and other unsupported
    objects therefore follow the recorder's ``str(value)`` fallback rather
    than being compared as in-memory objects.
    """
    if is_dataclass(value):
        return _recorded_json_projection(asdict(value))
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _recorded_json_projection(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_recorded_json_projection(v) for v in value]
    if isinstance(value, pd.DataFrame):
        return str(value)
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return str(value)


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
    expected_analytics=None,
    actual_market_context=None,
    tolerance: float = 1e-9,
) -> ReplayEquivalence:
    """Compare recorded and recomputed replay outputs.

    The optional analytics/context comparison validates the typed canonical
    MarketContext against the recorded analytics projection. Only canonical
    analytics fields actually present in the recorded artifact are compared,
    preserving compatibility with older snapshots that predate a field.
    """
    mismatches: list[str] = []

    expected_decision_normalized = _normalize(expected_decision)
    actual_decision_normalized = _normalize(actual_decision)
    if (
        isinstance(expected_decision_normalized, dict)
        and isinstance(actual_decision_normalized, dict)
        and "authoritative_signal" not in expected_decision_normalized
    ):
        # Legacy snapshots did not persist this execution-mutation
        # provenance field. Ignore only that metadata key so all other
        # canonical decision fields remain strictly comparable.
        actual_decision_normalized.pop("authoritative_signal", None)

    _compare(expected_decision_normalized, actual_decision_normalized, "decision", mismatches, tolerance)
    _compare(expected_intelligence, actual_intelligence, "intelligence", mismatches, tolerance)

    if isinstance(expected_analytics, dict) and actual_market_context is not None:
        canonical_fields = (
            "dealer",
            "dealer_flow",
            "liquidity",
            "gamma_flip",
            "gamma_wall",
            "oi_flow",
            "iv_skew",
            "iv_smile",
            "expected_move",
            "max_pain",
            "pcr",
            "market_structure",
            "atr",
            "volatility",
            "technical",
            "oi_shift",
            "probability",
            "signal",
            "institutional_score",
            "smart_strike",
            "trade_plan",
            "risk",
            "market_map",
        )
        expected_surface = {
            field_name: _recorded_json_projection(expected_analytics[field_name])
            for field_name in canonical_fields
            if field_name in expected_analytics
        }
        actual_surface = {
            field_name: _recorded_json_projection(getattr(actual_market_context, field_name))
            for field_name in expected_surface
        }
        _compare(expected_surface, actual_surface, "analytics", mismatches, tolerance)

    return ReplayEquivalence(not mismatches, tuple(mismatches))
