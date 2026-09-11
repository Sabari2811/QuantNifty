from types import SimpleNamespace

from dashboard.dashboard_controller import _effective_signal, _project_signal, _project_trade_plan


def _ctx(*, decision_signal="BUY", execution_status=None):
    status = SimpleNamespace(value=execution_status) if execution_status else None
    decision = SimpleNamespace(
        signal=SimpleNamespace(name=decision_signal, confidence=0.85),
        reasons=["analytical direction"],
    )
    execution_result = SimpleNamespace(status=status) if status else None
    market_context = SimpleNamespace(
        signal={"signal": decision_signal},
        trade_plan={
            "signal": decision_signal,
            "recommended_strike": 23400,
            "option_type": "PE",
            "strike_score": 80,
            "delta": -0.4,
            "iv": 0.2,
            "gex": 100,
            "entry": 100,
            "stop_loss": 90,
            "target1": 120,
            "target2": 130,
            "risk_reward": 3.0,
            "reasons": ["analytical setup"],
        },
    )
    return SimpleNamespace(
        decision=decision,
        execution_result=execution_result,
        market_context=market_context,
    )


def test_execution_veto_projects_wait_and_clears_actionable_fields():
    ctx = _ctx(decision_signal="BUY", execution_status="REJECTED")

    assert _effective_signal(ctx) == "WAIT"
    projected = _project_signal(ctx)
    assert projected["signal"] == "WAIT"
    assert projected["confidence"] == 0.0

    plan = _project_trade_plan(ctx)
    assert plan["signal"] == "WAIT"
    assert plan["recommended_strike"] is None
    assert plan["entry"] is None
    assert plan["stop_loss"] is None
    assert plan["target1"] is None
    assert plan["target2"] is None
    assert plan["option_type"] == ""


def test_non_vetoed_buy_remains_actionable():
    ctx = _ctx(decision_signal="BUY", execution_status=None)

    assert _effective_signal(ctx) == "BUY"
    projected = _project_signal(ctx)
    assert projected["signal"] == "BUY"
    assert projected["confidence"] == 0.85

    plan = _project_trade_plan(ctx)
    assert plan["signal"] == "BUY"
    assert plan["recommended_strike"] == 23400
    assert plan["entry"] == 100
