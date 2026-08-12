from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)
from analytics.intelligence.synthesis.regime_adjustment import (
    RegimeAwareIntelligence,
)


def test_trending_regime_reinforces_direction():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="TRENDING_UP",
        regime_confidence=100,
    )

    assert result.direction == "BULLISH"
    assert result.base_strength == 80
    assert result.adjusted_strength == 88
    assert result.adjusted_confidence == 99
    assert result.regime_multiplier == 1.10


def test_range_regime_reduces_conviction():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="RANGE",
        regime_confidence=100,
    )

    assert result.direction == "BULLISH"
    assert result.adjusted_strength == 64
    assert result.adjusted_confidence == 72


def test_transition_penalty_reduces_conviction():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="TRENDING_UP",
        regime_confidence=100,
        transition=True,
    )

    assert result.direction == "BULLISH"
    assert result.transition_penalty == 0.20
    assert result.adjusted_strength == 70.4
    assert result.adjusted_confidence == 79.2


def test_high_volatility_reduces_conviction():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="HIGH_VOLATILITY",
        regime_confidence=100,
    )

    assert result.adjusted_strength == 60
    assert result.adjusted_confidence == 67.5


def test_regime_confidence_scales_adjustment():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="TRENDING_UP",
        regime_confidence=50,
    )

    assert result.adjusted_strength == 44
    assert result.adjusted_confidence == 49.5


def test_unknown_regime_is_conservative():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    result = engine.adjust(
        synthesis,
        regime="UNKNOWN",
        regime_confidence=100,
    )

    assert result.adjusted_strength == 56
    assert result.adjusted_confidence == 63


def test_neutral_thesis_remains_neutral():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="NEUTRAL",
        strength=0,
        confidence=80,
        conflict_score=50,
    )

    result = engine.adjust(
        synthesis,
        regime="TRENDING_UP",
        regime_confidence=100,
    )

    assert result.direction == "NEUTRAL"
    assert result.adjusted_strength == 0


def test_regime_confidence_must_be_bounded():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=80,
        confidence=90,
    )

    try:
        engine.adjust(
            synthesis,
            regime="TRENDING_UP",
            regime_confidence=101,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for invalid regime confidence"
        )


def test_adjusted_values_are_bounded():
    engine = RegimeAwareIntelligence()

    synthesis = CrossFamilySynthesis(
        direction="BULLISH",
        strength=100,
        confidence=100,
    )

    result = engine.adjust(
        synthesis,
        regime="TRENDING_UP",
        regime_confidence=100,
    )

    assert 0 <= result.adjusted_strength <= 100
    assert 0 <= result.adjusted_confidence <= 100