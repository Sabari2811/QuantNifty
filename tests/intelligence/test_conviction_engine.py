from analytics.intelligence.synthesis.cross_family import (
    CrossFamilySynthesis,
)
from analytics.intelligence.synthesis.scenario.engine import (
    ScenarioEngine,
)
from analytics.intelligence.synthesis.conviction.engine import (
    ConvictionEngine,
)


def _synthesis(
    direction="BULLISH",
    strength=80.0,
    confidence=90.0,
    confluence=90.0,
    conflict=10.0,
    supporting=("GAMMA", "STRUCTURE", "OI_FLOW"),
    opposing=(),
):
    return CrossFamilySynthesis(
        direction=direction,
        strength=strength,
        confidence=confidence,
        confluence_score=confluence,
        conflict_score=conflict,
        supporting_families=supporting,
        opposing_families=opposing,
        family_count=len(supporting) + len(opposing),
    )


def test_strong_bullish_thesis_produces_positive_conviction():
    synthesis = _synthesis()

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="TRENDING_UP",
            confidence=100.0,
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert result.direction == "BULLISH"
    assert result.conviction > 0
    assert result.quality > 0
    assert result.conflict_level == 10.0


def test_direction_is_preserved():
    synthesis = _synthesis(
        direction="BEARISH",
        supporting=("GAMMA", "STRUCTURE"),
        opposing=(),
    )

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="TRENDING_DOWN",
            confidence=100.0,
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert result.direction == "BEARISH"


def test_neutral_thesis_has_zero_conviction():
    synthesis = _synthesis(
        direction="NEUTRAL",
        strength=0.0,
        confidence=90.0,
        confluence=50.0,
        conflict=50.0,
        supporting=(),
        opposing=("STRUCTURE",),
    )

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="RANGE",
            confidence=80.0,
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert result.direction == "NEUTRAL"
    assert result.conviction == 0.0
    assert result.quality == 0.0


def test_conflict_reduces_conviction():
    clean = _synthesis(
        conflict=0.0,
        confluence=100.0,
    )

    conflicted = _synthesis(
        conflict=50.0,
        confluence=50.0,
        supporting=("GAMMA", "STRUCTURE"),
        opposing=("VOLATILITY",),
    )

    regime_clean = _regime_adjustment(
        clean,
        regime="TRENDING_UP",
        confidence=100.0,
    )

    regime_conflicted = _regime_adjustment(
        conflicted,
        regime="TRENDING_UP",
        confidence=100.0,
    )

    scenario_engine = ScenarioEngine()

    clean_result = ConvictionEngine().evaluate(
        clean,
        scenario_engine.generate(
            clean,
            regime_clean,
        ),
    )

    conflicted_result = ConvictionEngine().evaluate(
        conflicted,
        scenario_engine.generate(
            conflicted,
            regime_conflicted,
        ),
    )

    assert conflicted_result.conviction < clean_result.conviction
    assert conflicted_result.conflict_level == 50.0


def test_more_independent_families_increase_independence_score():
    one = _synthesis(
        supporting=("GAMMA",),
    )

    three = _synthesis(
        supporting=("GAMMA", "STRUCTURE", "OI_FLOW"),
    )

    engine = ConvictionEngine()

    scenarios_one = ScenarioEngine().generate(
        one,
        _regime_adjustment(
            one,
            regime="TRENDING_UP",
        ),
    )

    scenarios_three = ScenarioEngine().generate(
        three,
        _regime_adjustment(
            three,
            regime="TRENDING_UP",
        ),
    )

    result_one = engine.evaluate(
        one,
        scenarios_one,
    )

    result_three = engine.evaluate(
        three,
        scenarios_three,
    )

    assert result_one.independence_score == 50.0
    assert result_three.independence_score == 85.0
    assert result_three.conviction > result_one.conviction


def test_scenario_direction_must_align():
    synthesis = _synthesis()

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="TRENDING_UP",
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert result.scenario_alignment > 0.0
    assert scenarios.primary is not None
    assert scenarios.primary.direction == synthesis.direction


def test_result_values_are_bounded():
    synthesis = _synthesis(
        strength=100.0,
        confidence=100.0,
        confluence=100.0,
        conflict=0.0,
    )

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="TRENDING_UP",
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert 0.0 <= result.conviction <= 100.0
    assert 0.0 <= result.quality <= 100.0
    assert 0.0 <= result.conflict_level <= 100.0


def test_explanation_contains_major_components():
    synthesis = _synthesis()

    scenarios = ScenarioEngine().generate(
        synthesis,
        _regime_adjustment(
            synthesis,
            regime="TRENDING_UP",
        ),
    )

    result = ConvictionEngine().evaluate(
        synthesis,
        scenarios,
    )

    assert "BULLISH" in result.explanation
    assert "Quality=" in result.explanation
    assert "independence=" in result.explanation
    assert "conflict=" in result.explanation
    assert "Primary scenario:" in result.explanation


def _regime_adjustment(
    synthesis,
    regime="TRENDING_UP",
    confidence=100.0,
):
    from analytics.intelligence.synthesis.regime_adjustment import (
        RegimeAwareIntelligence,
    )

    return RegimeAwareIntelligence().adjust(
        synthesis,
        regime=regime,
        regime_confidence=confidence,
    )