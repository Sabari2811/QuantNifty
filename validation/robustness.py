"""Deterministic robustness helpers for post-backtest analysis."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from validation.backtest_gates import BacktestMetrics, calculate_backtest_metrics


@dataclass(frozen=True)
class RegimeResult:
    regime: str
    metrics: BacktestMetrics


@dataclass(frozen=True)
class ParameterResult:
    parameters: tuple[tuple[str, Any], ...]
    metrics: BacktestMetrics


def evaluate_regimes(records: Iterable[Any], *, field: str = "regime") -> tuple[RegimeResult, ...]:
    groups: dict[str, list[Any]] = {}
    for row in records:
        value = row.get(field) if isinstance(row, dict) else getattr(row, field, None)
        if value is None:
            raise ValueError(f"missing_{field}")
        groups.setdefault(str(value), []).append(row)
    return tuple(RegimeResult(name, calculate_backtest_metrics(rows)) for name, rows in sorted(groups.items()))


def evaluate_parameter_runs(runs: Iterable[tuple[dict[str, Any], Iterable[Any]]]) -> tuple[ParameterResult, ...]:
    """Evaluate externally-produced parameter runs without selecting a winner."""
    results = []
    for parameters, records in runs:
        normalized = tuple(sorted(parameters.items(), key=lambda item: item[0]))
        results.append(ParameterResult(normalized, calculate_backtest_metrics(records)))
    return tuple(results)
