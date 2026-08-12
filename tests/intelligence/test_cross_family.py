from analytics.intelligence.synthesis.cross_family import (
    CrossFamilyConfluenceEngine,
)
from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidence,
)


def test_bullish_cross_family_confluence():
    engine = CrossFamilyConfluenceEngine()

    result = engine.synthesize(
        [
            FamilyEvidence(
                family="GAMMA",
                direction="BULLISH",
                strength=90,
                confidence=95,
            ),
            FamilyEvidence(
                family="STRUCTURE",
                direction="BULLISH",
                strength=85,
                confidence=90,
            ),
            FamilyEvidence(
                family="OI_FLOW",
                direction="BULLISH",
                strength=80,
                confidence=85,
            ),
        ]
    )

    assert result.direction == "BULLISH"
    assert result.confluence_score > 50
    assert result.conflict_score == 0
    assert result.family_count == 3


def test_cross_family_conflict_is_preserved():
    engine = CrossFamilyConfluenceEngine()

    result = engine.synthesize(
        [
            FamilyEvidence(
                family="GAMMA",
                direction="BULLISH",
                strength=80,
                confidence=90,
            ),
            FamilyEvidence(
                family="STRUCTURE",
                direction="BEARISH",
                strength=80,
                confidence=90,
            ),
        ]
    )

    assert result.direction == "NEUTRAL"
    assert result.conflict_score == 50
    assert result.supporting_families == ("GAMMA",)
    assert result.opposing_families == ("STRUCTURE",)


def test_bearish_cross_family_confluence():
    engine = CrossFamilyConfluenceEngine()

    result = engine.synthesize(
        [
            FamilyEvidence(
                family="GAMMA",
                direction="BEARISH",
                strength=90,
                confidence=90,
            ),
            FamilyEvidence(
                family="OI_FLOW",
                direction="BEARISH",
                strength=80,
                confidence=85,
            ),
            FamilyEvidence(
                family="TECHNICAL",
                direction="BULLISH",
                strength=30,
                confidence=70,
            ),
        ]
    )

    assert result.direction == "BEARISH"
    assert result.bearish_score > result.bullish_score
    assert result.conflict_score > 0


def test_empty_cross_family_input_is_neutral():
    engine = CrossFamilyConfluenceEngine()

    result = engine.synthesize([])

    assert result.direction == "NEUTRAL"
    assert result.strength == 0
    assert result.conflict_score == 0
    assert result.family_count == 0


def test_cross_family_metrics_are_bounded():
    engine = CrossFamilyConfluenceEngine()

    result = engine.synthesize(
        [
            FamilyEvidence(
                family="GAMMA",
                direction="BULLISH",
                strength=100,
                confidence=100,
            ),
            FamilyEvidence(
                family="STRUCTURE",
                direction="BEARISH",
                strength=100,
                confidence=100,
            ),
        ]
    )

    assert 0 <= result.strength <= 100
    assert 0 <= result.confidence <= 100
    assert 0 <= result.confluence_score <= 100
    assert 0 <= result.conflict_score <= 100