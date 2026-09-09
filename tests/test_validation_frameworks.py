from validation.backtest_gates import calculate_backtest_metrics, evaluate_backtest
from validation.certification_report import build_certification_report
from validation.data_leakage import validate_no_future_information
from validation.robustness import evaluate_parameter_runs, evaluate_regimes
from validation.strategy_contract import validate_strategy_records
from validation.walk_forward import validate_temporal_order, walk_forward_windows


def test_backtest_metrics_and_gates():
    rows = [{"pnl": 10}, {"pnl": -5}, {"pnl": 20}, {"pnl": -2}]
    metrics = calculate_backtest_metrics(rows)
    assert metrics.trades == 4
    assert metrics.wins == 2
    assert metrics.losses == 2
    assert metrics.total_pnl == 23
    assert metrics.profit_factor == 30 / 7
    assert metrics.max_drawdown == 5
    assert evaluate_backtest(rows, min_trades=4, min_profit_factor=2, min_expectancy=5).passed


def test_strategy_contract_enforces_three_trades_and_execution_gates():
    rows = [
        {"timestamp": "2026-09-09T09:20:00+05:30", "actionable": True, "risk_allowed": True, "execution_status": "EXECUTED"},
        {"timestamp": "2026-09-09T10:20:00+05:30", "actionable": True, "risk_allowed": True, "execution_status": "EXECUTED"},
        {"timestamp": "2026-09-09T11:20:00+05:30", "actionable": True, "risk_allowed": True, "execution_status": "EXECUTED"},
    ]
    assert validate_strategy_records(rows).passed
    bad = rows + [{"timestamp": "2026-09-09T12:20:00+05:30", "actionable": True, "risk_allowed": True, "execution_status": "EXECUTED"}]
    assert not validate_strategy_records(bad).passed
    blocked = [{"timestamp": "2026-09-09T09:20:00+05:30", "actionable": False, "risk_allowed": False, "execution_status": "EXECUTED"}]
    assert not validate_strategy_records(blocked).passed


def test_walk_forward_is_ordered_and_non_overlapping():
    rows = list(range(10))
    windows = walk_forward_windows(rows, train_size=4, test_size=2)
    assert len(windows) == 3
    assert windows[0].train == (0, 1, 2, 3)
    assert windows[0].test == (4, 5)
    assert windows[1].train == (2, 3, 4, 5)
    assert windows[1].test == (6, 7)
    assert validate_temporal_order([{"timestamp": "2026-01-01"}, {"timestamp": "2026-01-02"}])[0]
    assert not validate_temporal_order([{"timestamp": "2026-01-02"}, {"timestamp": "2026-01-01"}])[0]


def test_leakage_gate_rejects_future_features_and_early_outcomes():
    good = [{"feature_timestamp": "2026-01-01T09:00:00+05:30", "decision_timestamp": "2026-01-01T09:01:00+05:30", "outcome_timestamp": "2026-01-01T09:02:00+05:30"}]
    assert validate_no_future_information(good)[0]
    future_feature = [dict(good[0], feature_timestamp="2026-01-01T09:03:00+05:30")]
    assert not validate_no_future_information(future_feature)[0]
    early_outcome = [dict(good[0], outcome_timestamp="2026-01-01T09:00:30+05:30")]
    assert not validate_no_future_information(early_outcome)[0]


def test_regime_and_parameter_evaluators_do_not_select_or_mutate():
    rows = [{"regime": "TREND", "pnl": 5}, {"regime": "RANGE", "pnl": -2}, {"regime": "TREND", "pnl": 3}]
    regimes = evaluate_regimes(rows)
    assert [item.regime for item in regimes] == ["RANGE", "TREND"]
    runs = evaluate_parameter_runs([({"threshold": 1}, [{"pnl": 1}]), ({"threshold": 2}, [{"pnl": 2}])])
    assert len(runs) == 2
    assert runs[0].parameters == (("threshold", 1),)


def test_final_report_is_fail_closed_until_every_gate_passes():
    report = build_certification_report(
        live_certification=True,
        strategy_contract=True,
        backtest_gate=True,
        temporal_integrity=True,
        walk_forward=None,
        robustness=True,
    )
    assert report.overall == "NOT_CERTIFIED"
    complete = build_certification_report(
        live_certification=True,
        strategy_contract=True,
        backtest_gate=True,
        temporal_integrity=True,
        walk_forward=True,
        robustness=True,
    )
    assert complete.overall == "PASS"
