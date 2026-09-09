"""Orchestrate deterministic after-market strategy validation.

This layer consumes recorded strategy/backtest outputs only. It never runs a
broker and never changes the strategy's decisions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from validation.backtest_gates import BacktestGateResult, evaluate_backtest
from validation.certification_report import CertificationReport, build_certification_report
from validation.data_leakage import validate_no_future_information
from validation.robustness import RegimeResult, evaluate_regimes
from validation.strategy_contract import StrategyContractResult, validate_strategy_records
from validation.walk_forward import WalkForwardWindow, validate_temporal_order, walk_forward_windows


@dataclass(frozen=True)
class AfterMarketResult:
    strategy_contract: StrategyContractResult
    backtest_gate: BacktestGateResult
    temporal_integrity: tuple[bool, tuple[str, ...]]
    leakage: tuple[bool, tuple[str, ...]]
    walk_forward_windows: tuple[WalkForwardWindow, ...]
    regimes: tuple[RegimeResult, ...]
    certification: CertificationReport


def validate_after_market(
    records: Sequence[dict[str, Any]] | Iterable[dict[str, Any]],
    *,
    min_trades: int = 1,
    max_trades_per_day: int | None = 3,
    train_size: int = 20,
    test_size: int = 5,
) -> AfterMarketResult:
    rows = tuple(records)
    contract = validate_strategy_records(rows, max_trades_per_day=max_trades_per_day)
    backtest = evaluate_backtest(rows, min_trades=min_trades)
    temporal = validate_temporal_order(rows)
    leakage = validate_no_future_information(rows)
    windows = walk_forward_windows(rows, train_size=train_size, test_size=test_size)
    regimes = evaluate_regimes(rows) if rows and all("regime" in row for row in rows) else ()
    certification = build_certification_report(
        strategy_contract=contract,
        backtest_gate=backtest,
        temporal_integrity=temporal[0],
        walk_forward=bool(windows),
        robustness=bool(regimes),
        notes=("Live certification is intentionally excluded; it requires genuine market evidence.",),
    )
    return AfterMarketResult(contract, backtest, temporal, leakage, windows, regimes, certification)
