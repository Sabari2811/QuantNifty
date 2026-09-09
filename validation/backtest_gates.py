"""Deterministic, dependency-free backtest validation gates.

The module evaluates already-produced trade outcomes. It does not generate
signals or alter strategy decisions, making it safe to use after-market and in
historical replay validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable


@dataclass(frozen=True)
class BacktestMetrics:
    trades: int
    wins: int
    losses: int
    win_rate_pct: float
    total_pnl: float
    gross_profit: float
    gross_loss: float
    profit_factor: float
    expectancy_per_trade: float
    average_win: float
    average_loss: float
    max_drawdown: float
    max_consecutive_losses: int


@dataclass(frozen=True)
class BacktestGateResult:
    passed: bool
    metrics: BacktestMetrics
    reasons: tuple[str, ...]


def _pnl_rows(records: Iterable[Any]) -> list[float]:
    values: list[float] = []
    for index, row in enumerate(records, start=1):
        value = row.get("pnl") if isinstance(row, dict) else getattr(row, "pnl", None)
        try:
            pnl = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"trade_{index}:pnl_missing_or_invalid") from None
        if not isfinite(pnl):
            raise ValueError(f"trade_{index}:pnl_missing_or_invalid")
        values.append(pnl)
    return values


def calculate_backtest_metrics(records: Iterable[Any]) -> BacktestMetrics:
    pnls = _pnl_rows(records)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    total = sum(pnls)
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss else (float("inf") if gross_profit else 0.0)

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    consecutive = 0
    max_consecutive = 0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
        if pnl < 0:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0

    return BacktestMetrics(
        trades=len(pnls),
        wins=len(wins),
        losses=len(losses),
        win_rate_pct=(len(wins) / len(pnls) * 100.0) if pnls else 0.0,
        total_pnl=total,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        profit_factor=profit_factor,
        expectancy_per_trade=(total / len(pnls)) if pnls else 0.0,
        average_win=(gross_profit / len(wins)) if wins else 0.0,
        average_loss=(sum(losses) / len(losses)) if losses else 0.0,
        max_drawdown=max_drawdown,
        max_consecutive_losses=max_consecutive,
    )


def evaluate_backtest(
    records: Iterable[Any],
    *,
    min_trades: int = 1,
    min_win_rate_pct: float | None = None,
    min_profit_factor: float | None = None,
    min_expectancy: float | None = None,
    max_drawdown: float | None = None,
    max_consecutive_losses: int | None = None,
) -> BacktestGateResult:
    """Apply explicit acceptance thresholds; unspecified thresholds are not inferred."""
    if min_trades < 1:
        raise ValueError("min_trades must be >= 1")
    metrics = calculate_backtest_metrics(records)
    reasons: list[str] = []
    if metrics.trades < min_trades:
        reasons.append(f"insufficient_trades:{metrics.trades}<{min_trades}")
    if min_win_rate_pct is not None and metrics.win_rate_pct < min_win_rate_pct:
        reasons.append(f"win_rate_below_threshold:{metrics.win_rate_pct:.4f}<{min_win_rate_pct}")
    if min_profit_factor is not None and metrics.profit_factor < min_profit_factor:
        reasons.append(f"profit_factor_below_threshold:{metrics.profit_factor:.4f}<{min_profit_factor}")
    if min_expectancy is not None and metrics.expectancy_per_trade < min_expectancy:
        reasons.append(f"expectancy_below_threshold:{metrics.expectancy_per_trade:.4f}<{min_expectancy}")
    if max_drawdown is not None and metrics.max_drawdown > max_drawdown:
        reasons.append(f"drawdown_above_threshold:{metrics.max_drawdown:.4f}>{max_drawdown}")
    if max_consecutive_losses is not None and metrics.max_consecutive_losses > max_consecutive_losses:
        reasons.append(f"consecutive_losses_above_threshold:{metrics.max_consecutive_losses}>{max_consecutive_losses}")
    return BacktestGateResult(not reasons, metrics, tuple(reasons))
