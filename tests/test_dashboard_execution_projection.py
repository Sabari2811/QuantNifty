from types import SimpleNamespace

from dashboard.dashboard_controller import _effective_signal, _project_signal, _project_trade_plan


def _ctx(signal="WAIT"):
    return SimpleNamespace(
        decision=SimpleNamespace(
            signal=SimpleNamespace(name=signal, confidence=85.0),
            reasons=["validation"],
        ),
        market_context=SimpleNamespace(
            signal={"signal": "BUY PUT", "confidence": 85.0},
            trade_plan={
                "signal": "BUY PUT",
                "recommended_strike": 23400,
                "option_type": "PE",
                "strike_score": 132.8,
                "delta": -0.43,
                "iv": 0.10,
                "gex": -100.0,
                "entry": 23445,
                "stop_loss": 23552.08,
                "target1": 23284.38,
                "target2": 23123.76,
                "risk_reward": 3.0,
                "atr": 107.08,
                "volatility": "NORMAL",
                "reasons": ["Gamma support"],
            },
        ),
    )


def test_wait_projects_post_validation_state_and_removes_active_levels():
    ctx = _ctx("WAIT")

    assert _effective_signal(ctx) == "WAIT"
    assert _project_signal(ctx)["signal"] == "WAIT"

    plan = _project_trade_plan(ctx)
    assert plan["signal"] == "WAIT"
    assert plan["recommended_strike"] is None
    assert plan["option_type"] == ""
    assert plan["entry"] is None
    assert plan["stop_loss"] is None
    assert plan["target1"] is None
    assert plan["target2"] is None
    assert plan["risk_reward"] is None
    assert plan["atr"] == 107.08
    assert plan["volatility"] == "NORMAL"


def test_actionable_signal_preserves_canonical_trade_plan():
    ctx = _ctx("BUY PUT")
    plan = _project_trade_plan(ctx)

    assert _effective_signal(ctx) == "BUY PUT"
    assert plan["signal"] == "BUY PUT"
    assert plan["recommended_strike"] == 23400
    assert plan["option_type"] == "PE"
    assert plan["entry"] == 23445


def test_projection_does_not_mutate_market_context():
    ctx = _ctx("WAIT")
    original = dict(ctx.market_context.trade_plan)

    _project_trade_plan(ctx)

    assert ctx.market_context.trade_plan == original
