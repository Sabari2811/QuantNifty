from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)
from analytics.intelligence.synthesis.regime_adjustment import (
    RegimeAdjustment,
)
from analytics.intelligence.synthesis.scenario.engine import (
    ScenarioEngine,
)


def test_bullish_thesis_creates_bullish_primary():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
        confluence_score=80,
        conflict_score=20,
    )

    regime = RegimeAdjustment(
        regime="TRENDING_UP",
        direction="BULLISH",
        base_strength=80,
        adjusted_strength=88,
        base_confidence=90,
        adjusted_confidence=99,
        regime_multiplier=1.10,
    )

    result = engine.generate(synthesis, regime)

    assert result.direction == "BULLISH"
    assert result.primary is not None
    assert result.alternative is not None

    assert result.primary.direction == "BULLISH"
    assert result.alternative.direction == "BEARISH"


def test_bearish_thesis_creates_bearish_primary():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BEARISH",
        strength=80,
        confidence=90,
        confluence_score=80,
        conflict_score=20,
    )

    regime = RegimeAdjustment(
        regime="TRENDING_DOWN",
        direction="BEARISH",
        base_strength=80,
        adjusted_strength=88,
        base_confidence=90,
        adjusted_confidence=99,
        regime_multiplier=1.10,
    )

    result = engine.generate(synthesis, regime)

    assert result.direction == "BEARISH"
    assert result.primary.direction == "BEARISH"
    assert result.alternative.direction == "BULLISH"


def test_scenario_probabilities_sum_to_100():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=75,
        confidence=80,
        confluence_score=75,
        conflict_score=25,
    )

    regime = RegimeAdjustment(
        regime="TRENDING_UP",
        direction="BULLISH",
        base_strength=75,
        adjusted_strength=82.5,
        base_confidence=80,
        adjusted_confidence=88,
        regime_multiplier=1.10,
    )

    result = engine.generate(synthesis, regime)

    total = (
        result.primary.probability
        + result.alternative.probability
    )

    assert total == 100.0


def test_stronger_thesis_gets_higher_primary_probability():
    engine = ScenarioEngine()

    weak = CrossFamilySynthesis(
        direction="BULLISH",
        strength=60,
        confidence=70,
        confluence_score=60,
        conflict_score=40,
    )

    strong = CrossFamilySynthesis(
        direction="BULLISH",
        strength=85,
        confidence=90,
        confluence_score=90,
        conflict_score=10,
    )

    regime_weak = RegimeAdjustment(
        regime="RANGE",
        direction="BULLISH",
        base_strength=60,
        adjusted_strength=48,
        base_confidence=70,
        adjusted_confidence=56,
        regime_multiplier=0.80,
    )

    regime_strong = RegimeAdjustment(
        regime="TRENDING_UP",
        direction="BULLISH",
        base_strength=85,
        adjusted_strength=93.5,
        base_confidence=90,
        adjusted_confidence=99,
        regime_multiplier=1.10,
    )

    weak_result = engine.generate(weak, regime_weak)
    strong_result = engine.generate(strong, regime_strong)

    assert (
        strong_result.primary.probability
        > weak_result.primary.probability
    )


def test_neutral_thesis_produces_balanced_scenarios():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="NEUTRAL",
        strength=0,
        confidence=70,
        confluence_score=50,
        conflict_score=50,
    )

    regime = RegimeAdjustment(
        regime="RANGE",
        direction="NEUTRAL",
        base_strength=0,
        adjusted_strength=0,
        base_confidence=70,
        adjusted_confidence=56,
        regime_multiplier=0.80,
    )

    result = engine.generate(synthesis, regime)

    assert result.direction == "NEUTRAL"
    assert result.primary.direction == "NEUTRAL"
    assert result.alternative.direction == "NEUTRAL"
    assert result.primary.probability == 50
    assert result.alternative.probability == 50


def test_scenario_confidence_is_regime_adjusted_confidence():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=70,
        confidence=80,
    )

    regime = RegimeAdjustment(
        regime="RANGE",
        direction="BULLISH",
        base_strength=70,
        adjusted_strength=56,
        base_confidence=80,
        adjusted_confidence=64,
        regime_multiplier=0.80,
    )

    result = engine.generate(synthesis, regime)

    assert result.confidence == 64


def test_primary_probability_is_bounded():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=100,
        confidence=100,
        confluence_score=100,
        conflict_score=0,
    )

    regime = RegimeAdjustment(
        regime="TRENDING_UP",
        direction="BULLISH",
        base_strength=100,
        adjusted_strength=100,
        base_confidence=100,
        adjusted_confidence=100,
        regime_multiplier=1.10,
    )

    result = engine.generate(synthesis, regime)

    assert 55 <= result.primary.probability <= 85
    assert 15 <= result.alternative.probability <= 45


def test_primary_and_alternative_have_triggers_and_invalidations():
    engine = ScenarioEngine()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    regime = RegimeAdjustment(
        regime="BREAKOUT",
        direction="BULLISH",
        base_strength=80,
        adjusted_strength=84,
        base_confidence=90,
        adjusted_confidence=94.5,
        regime_multiplier=1.05,
    )

    result = engine.generate(synthesis, regime)

    assert result.primary.trigger
    assert result.primary.invalidation
    assert result.primary.rationale

    assert result.alternative.trigger
    assert result.alternative.invalidation
    assert result.alternative.rationale