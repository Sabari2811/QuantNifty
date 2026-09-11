from decision.execution.delta_risk import DeltaRiskModel


def test_delta_translates_underlying_move_to_premium_move():
    model = DeltaRiskModel()
    assert model.premium_move(0.5, 100) == 50.0


def test_levels_respect_250_point_trade_horizon():
    model = DeltaRiskModel()
    stop, target1, target2 = model.levels(100.0, 0.4)
    assert stop == 60.0
    assert target1 == 160.0
    assert target2 == 200.0


def test_zero_delta_cannot_create_risk_levels():
    model = DeltaRiskModel()
    assert model.levels(100.0, 0.0) == (0.0, 0.0, 0.0)


def test_trade_horizon_cannot_exceed_daily_horizon():
    try:
        DeltaRiskModel(max_daily_underlying_points=200.0, max_trade_underlying_points=250.0)
    except ValueError as exc:
        assert "Trade movement cap" in str(exc)
    else:
        raise AssertionError("Expected invalid movement configuration")
