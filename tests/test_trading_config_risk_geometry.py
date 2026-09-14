from config.trading_config import TradingConfig


def test_default_nifty_target1_clears_strict_rr_floor_in_all_iv_regimes():
    multiplier = TradingConfig.TARGET1_MULTIPLIER
    for stop_pct in (
        TradingConfig.STOPLOSS_LOW_IV,
        TradingConfig.STOPLOSS_NORMAL_IV,
        TradingConfig.STOPLOSS_HIGH_IV,
    ):
        rr = (multiplier - 1.0) / stop_pct
        assert rr > TradingConfig.MIN_RISK_REWARD


def test_default_nifty_trade_move_stays_within_max_trade_move():
    assert TradingConfig.TARGET2_UNDERLYING_POINTS <= TradingConfig.MAX_TRADE_UNDERLYING_MOVE


def test_execution_thresholds_are_centralized_and_positive():
    assert TradingConfig.MIN_OPTION_PREMIUM > 0
    assert TradingConfig.MIN_OPTION_OI > 0
    assert TradingConfig.MIN_OPTION_VOLUME > 0
    assert TradingConfig.MAX_OPTION_RISK_PERCENT > 0
    assert TradingConfig.NIFTY_LOT_SIZE > 0
