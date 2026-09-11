from types import SimpleNamespace

from backtesting.performance_analyzer import PerformanceAnalyzer


def _trade(pnl, risk_reward, holding_seconds):
    return SimpleNamespace(
        pnl=pnl,
        risk_reward=risk_reward,
        holding_seconds=holding_seconds,
    )


def test_performance_analyzer_populates_extended_metrics():
    trades = [
        _trade(100.0, 2.0, 600),
        _trade(-50.0, 1.5, 1200),
        _trade(50.0, 2.5, 1800),
    ]

    metrics = PerformanceAnalyzer().analyze(trades, starting_capital=10_000.0)

    assert metrics.net_profit == 100.0
    assert metrics.average_risk_reward == 2.0
    assert metrics.average_holding_minutes == 20.0
    assert metrics.roi_percent == 1.0
    assert metrics.sharpe_ratio != 0.0
    assert metrics.sortino_ratio != 0.0


def test_risk_ratios_remain_zero_when_variance_is_not_supported():
    trades = [_trade(100.0, 2.0, 60), _trade(100.0, 2.0, 60)]

    metrics = PerformanceAnalyzer().analyze(trades, starting_capital=10_000.0)

    assert metrics.sharpe_ratio == 0.0
    assert metrics.sortino_ratio == 0.0
