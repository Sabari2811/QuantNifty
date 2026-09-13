from config.trading_config import TradingConfig
from decision.execution.trade_validator import TradeValidator
from decision.models import Decision
from decision.models.option_contract import OptionContract
from decision.validation_result import ValidationResult


def make_decision(*, risk_reward=1.80, oi=125000, volume=98000, entry=182.45, score=None):
    decision = Decision()
    decision.trade.entry = entry
    decision.trade.risk_reward = risk_reward
    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=entry,
        oi=oi,
        volume=volume,
    )
    decision.score = score if score is not None else {"quality_score": 80}
    return decision


def test_trade_validator_returns_validation_result():
    decision = make_decision(risk_reward=1.60, score={"final": 80})

    result = TradeValidator().validate(decision)

    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert result.grade == "B"
    assert result.confidence == 80
    assert result.risk_multiplier == 0.50
    assert result.warnings == []


def test_trade_validator_rejects_risk_reward_at_or_below_threshold():
    for risk_reward in (TradingConfig.MIN_RISK_REWARD, 1.40):
        result = TradeValidator().validate(
            make_decision(risk_reward=risk_reward)
        )
        assert result.valid is False
        assert result.warnings == [
            f"Risk/Reward must be above {TradingConfig.MIN_RISK_REWARD}"
        ]


def test_trade_validator_uses_quality_not_signed_directional_score():
    decision = make_decision(
        risk_reward=1.80,
        score={
            "quality_score": 69,
            "signed_score": -69,
            "final": -36,
        },
    )

    result = TradeValidator().validate(decision)

    assert result.valid is True
    assert result.grade == "C"
    assert result.confidence == 70
    assert result.risk_multiplier == 0.25


def test_trade_validator_uses_centralized_volume_threshold():
    decision = make_decision(volume=TradingConfig.MIN_OPTION_VOLUME - 1)

    result = TradeValidator().validate(decision)

    assert result.valid is False
    assert "Low Volume" in result.warnings
