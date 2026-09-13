from config.trading_config import TradingConfig


def test_default_nifty_risk_geometry_clears_strict_rr_floor():
    rr = (
        TradingConfig.TARGET1_UNDERLYING_POINTS
        / TradingConfig.STOP_UNDERLYING_POINTS
    )

    assert rr > TradingConfig.MIN_RISK_REWARD


def test_default_nifty_trade_move_stays_within_max_trade_move():
    assert TradingConfig.TARGET2_UNDERLYING_POINTS <= TradingConfig.MAX_TRADE_UNDERLYING_MOVE
