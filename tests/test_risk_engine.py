from decision.models import Decision
from decision.models.option_contract import OptionContract
from decision.execution.risk_engine import RiskEngine


def test_risk_engine_builds_stop_loss_and_risk_reward_from_contract():
    decision = Decision()
    decision.trade.entry = 182.45
    decision.trade.target1 = 220.00

    contract = OptionContract(strike=24400, option_type="CE", ltp=182.45, iv=22)

    engine = RiskEngine()
    result = engine.build(decision, contract)

    expected_stop = round(contract.ltp * (1 - engine._risk_percent(contract.iv)), 2)
    expected_rr = round(
        (decision.trade.target1 - decision.trade.entry)
        / (decision.trade.entry - expected_stop),
        2,
    )

    assert result is decision
    assert result.trade.stop_loss == expected_stop
    assert result.trade.risk_reward == expected_rr
    assert result.trade.stop_loss < result.trade.entry
    assert result.trade.risk_reward > 0
