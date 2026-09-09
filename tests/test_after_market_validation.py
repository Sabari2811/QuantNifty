from validation.after_market import validate_after_market


def _rows(count=25):
    rows = []
    for i in range(count):
        minute = i + 1
        rows.append({
            "timestamp": f"2026-09-09T09:{minute:02d}:00+05:30",
            "decision_timestamp": f"2026-09-09T09:{minute:02d}:00+05:30",
            "feature_timestamp": f"2026-09-09T09:{max(0, minute-1):02d}:00+05:30",
            "outcome_timestamp": f"2026-09-09T10:{minute:02d}:00+05:30",
            "pnl": 10 if i % 2 == 0 else -5,
            "actionable": True,
            "risk_allowed": True,
            "execution_status": "EXECUTED",
            "regime": "TREND" if i % 2 == 0 else "RANGE",
        })
    return rows


def test_after_market_validation_produces_all_independent_outputs():
    result = validate_after_market(_rows(), min_trades=20, train_size=20, test_size=5)
    assert result.strategy_contract.passed
    assert result.backtest_gate.passed
    assert result.temporal_integrity[0]
    assert result.leakage[0]
    assert result.walk_forward_windows
    assert result.regimes
    # Live certification is intentionally not produced from historical records.
    assert result.certification.overall == "NOT_CERTIFIED"
