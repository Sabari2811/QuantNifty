from decision.models import Decision
from decision.option_contract import OptionContract
from decision.execution.premium.premium_engine import PremiumEngine
from config.trading_config import TradingConfig


def test_premium_engine_builds_levels_from_contract():
    decision = Decision()
    contract = OptionContract(strike=24400, option_type="CE", ltp=182.45)

    result = PremiumEngine().build(decision, contract)

    assert result is decision
    assert result.trade.entry == 182.45
    assert result.trade.target1 == round(182.45 * TradingConfig.TARGET1_MULTIPLIER, 2)
    assert result.trade.target2 == round(182.45 * TradingConfig.TARGET2_MULTIPLIER, 2)
    assert result.trade.target1 > result.trade.entry
    assert result.trade.target2 > result.trade.target1
