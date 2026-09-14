from config.trading_config import TradingConfig
from decision.execution.premium.premium_engine import PremiumEngine
from decision.execution.risk_engine import RiskEngine
from decision.models import Decision
from decision.models.option_contract import OptionContract


def test_default_target1_clears_strict_rr_for_high_iv_contract():
    decision = Decision()
    contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=100.0,
        iv=TradingConfig.HIGH_IV_THRESHOLD,
    )

    PremiumEngine().build(decision, contract)
    RiskEngine().build(decision, contract)

    assert decision.trade.target1 == 155.0
    assert decision.trade.stop_loss == 70.0
    assert decision.trade.risk_reward > TradingConfig.MIN_RISK_REWARD
