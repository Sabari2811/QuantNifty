from datetime import datetime, timedelta

from validation.after_market import validate_after_market


def _rows(count=25):
    rows = []
    start = datetime.fromisoformat("2026-09-09T09:30:00+05:30")
    for i in range(count):
        # Keep the synthetic fixture inside the real strategy contract:
        # no more than three executed trades per trading day.
        day_offset = i // 3
        slot = i % 3
        decision = start + timedelta(days=day_offset, minutes=slot * 10)
        feature = decision - timedelta(minutes=1)
        outcome = decision + timedelta(minutes=30)
        rows.append({
            "timestamp": decision.isoformat(),
            "decision_timestamp": decision.isoformat(),
            "feature_timestamp": feature.isoformat(),
            "outcome_timestamp": outcome.isoformat(),
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
