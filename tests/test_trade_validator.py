from decision.execution.trade_validator import TradeValidator
from decision.models import Decision
from decision.models.option_contract import OptionContract
from decision.validation_result import ValidationResult


def test_trade_validator_rejects_rr_at_or_below_configured_floor():
    decision = Decision()
    decision.trade.entry = 182.45
    decision.trade.risk_reward = 1.50
    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=182.45,
        oi=125000,
        volume=98000,
    )
    decision.score = {"final": 80}

    result = TradeValidator().validate(decision)

    assert isinstance(result, ValidationResult)
    assert result.valid is False
    assert result.grade == "B"
    assert result.confidence == 80
    assert result.risk_multiplier == 0.50
    assert result.warnings == ["Risk/Reward must be greater than 1.5"]


def test_trade_validator_uses_quality_not_signed_directional_score():
    decision = Decision()

    decision.trade.entry = 182.45
    decision.trade.risk_reward = 1.80

    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="PE",
        ltp=182.45,
        oi=125000,
        volume=98000,
    )

    decision.score = {
        "quality_score": 69,
        "signed_score": -69,
        "final": -36,
    }

    result = TradeValidator().validate(decision)

    assert result.valid is True
    assert result.grade == "C"
    assert result.confidence == 70
    assert result.risk_multiplier == 0.25
