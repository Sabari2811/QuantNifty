from decision.models import Decision
from decision.models.option_contract import OptionContract

from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)

from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidence,
)

from analytics.intelligence.synthesis.orchestration.engine import (
    IntelligenceSynthesisEngine,
)


def _decision():
    decision = Decision()

    decision.trade.risk_reward = 2.0

    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=182.45,
        iv=12.6,
        oi=125000,
        volume=98000,
        delta=0.42,
    )

    return decision


def _families():
    return [
        FamilyEvidence(
            family="GAMMA",
            direction="BULLISH",
            strength=80.0,
            confidence=90.0,
            freshness=100.0,
        ),
        FamilyEvidence(
            family="STRUCTURE",
            direction="BULLISH",
            strength=75.0,
            confidence=85.0,
            freshness=100.0,
        ),
        FamilyEvidence(
            family="OI_FLOW",
            direction="BEARISH",
            strength=40.0,
            confidence=70.0,
            freshness=100.0,
        ),
    ]


def test_complete_synthesis_pipeline():
    engine = IntelligenceSynthesisEngine()

    result = engine.synthesize(
        families=_families(),
        decision=_decision(),
        regime="TRENDING_UP",
        regime_confidence=90.0,
        transition=False,
    )

    assert result.cross_family.direction == "BULLISH"

    assert result.regime.direction == "BULLISH"

    assert result.scenarios.primary is not None
    assert result.scenarios.alternative is not None

    assert result.conviction.direction == "BULLISH"

    assert result.opportunity.contract_available is True

    assert 0.0 <= result.opportunity.score <= 100.0


def test_pipeline_preserves_cross_family_direction():
    engine = IntelligenceSynthesisEngine()

    result = engine.synthesize(
        families=_families(),
        decision=_decision(),
        regime="TRENDING_UP",
    )

    assert (
        result.conviction.direction
        == result.cross_family.direction
    )


def test_pipeline_does_not_create_buy_sell():
    engine = IntelligenceSynthesisEngine()

    result = engine.synthesize(
        families=_families(),
        decision=_decision(),
        regime="TRENDING_UP",
    )

    assert result.cross_family.direction in {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    }

    assert result.conviction.direction in {
        "BULLISH",
        "BEARISH",
        "NEUTRAL",
    }