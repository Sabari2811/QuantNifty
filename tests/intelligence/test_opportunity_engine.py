from decision.models import Decision
from decision.models.option_contract import OptionContract

from analytics.intelligence.synthesis.opportunity.engine import (
    OpportunityQualityEngine,
)


def _decision(
    *,
    risk_reward: float = 1.40,
    iv: float = 12.6,
    oi: int = 125_000,
    volume: int = 98_000,
    delta: float = 0.42,
) -> Decision:
    decision = Decision()

    decision.trade.risk_reward = risk_reward

    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=182.45,
        iv=iv,
        oi=oi,
        volume=volume,
        delta=delta,
    )

    return decision


def test_legacy_fixture_produces_80():
    result = OpportunityQualityEngine().evaluate(
        _decision()
    )

    assert result.score == 80
    assert result.risk_reward_score == 10
    assert result.volatility_score == 20
    assert result.open_interest_score == 20
    assert result.volume_score == 20
    assert result.delta_score == 10
    assert result.contract_available is True


def test_no_contract_returns_zero():
    decision = Decision()

    result = OpportunityQualityEngine().evaluate(
        decision
    )

    assert result.score == 0
    assert result.contract_available is False
    assert result.reasons == (
        "No option contract is available",
    )


def test_risk_reward_thresholds():
    engine = OpportunityQualityEngine()

    assert engine.score(
        _decision(risk_reward=0.99)
    ) == 70

    assert engine.score(
        _decision(risk_reward=1.00)
    ) == 80

    assert engine.score(
        _decision(risk_reward=1.50)
    ) == 90

    assert engine.score(
        _decision(risk_reward=2.00)
    ) == 100

def test_iv_thresholds():
    engine = OpportunityQualityEngine()

    assert engine.score(
        _decision(iv=4.99)
    ) == 60

    assert engine.score(
        _decision(iv=5.00)
    ) == 70

    assert engine.score(
        _decision(iv=9.99)
    ) == 70

    assert engine.score(
        _decision(iv=10.00)
    ) == 80

    assert engine.score(
        _decision(iv=25.00)
    ) == 80

    assert engine.score(
        _decision(iv=25.01)
    ) == 60


def test_open_interest_thresholds():
    engine = OpportunityQualityEngine()

    assert engine.score(
        _decision(oi=49_999)
    ) == 60

    assert engine.score(
        _decision(oi=50_000)
    ) == 70

    assert engine.score(
        _decision(oi=100_000)
    ) == 80


def test_volume_thresholds():
    engine = OpportunityQualityEngine()

    assert engine.score(
        _decision(volume=19_999)
    ) == 60

    assert engine.score(
        _decision(volume=20_000)
    ) == 70

    assert engine.score(
        _decision(volume=50_000)
    ) == 80


def test_delta_uses_absolute_value():
    engine = OpportunityQualityEngine()

    assert engine.score(
        _decision(delta=0.29)
    ) == 70

    assert engine.score(
        _decision(delta=0.30)
    ) == 80

    assert engine.score(
        _decision(delta=-0.42)
    ) == 80

    assert engine.score(
        _decision(delta=0.70)
    ) == 80

    assert engine.score(
        _decision(delta=0.71)
    ) == 70


def test_score_is_bounded_at_100():
    engine = OpportunityQualityEngine()

    result = engine.evaluate(
        _decision(
            risk_reward=2.50,
            iv=15.0,
            oi=200_000,
            volume=100_000,
            delta=0.50,
        )
    )

    assert result.score == 100
    assert sum(
        (
            result.risk_reward_score,
            result.volatility_score,
            result.open_interest_score,
            result.volume_score,
            result.delta_score,
        )
    ) == 100


def test_reasons_expose_each_scoring_dimension():
    result = OpportunityQualityEngine().evaluate(
        _decision()
    )

    assert len(result.reasons) == 5
    assert "Risk/reward" in result.reasons[0]
    assert "IV" in result.reasons[1]
    assert "OI" in result.reasons[2]
    assert "Volume" in result.reasons[3]
    assert "Delta" in result.reasons[4]
