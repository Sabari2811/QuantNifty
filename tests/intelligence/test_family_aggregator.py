from analytics.intelligence.result import EvidenceItem
from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidenceAggregator,
)


def test_correlated_gamma_signals_create_one_family():
    aggregator = FamilyEvidenceAggregator()

    result = aggregator.aggregate(
        [
            EvidenceItem(
                source_family="Gamma",
                feature="GEX",
                direction="BULLISH",
                strength=80,
                confidence=90,
            ),
            EvidenceItem(
                source_family="Gamma",
                feature="gamma_flip",
                direction="BULLISH",
                strength=75,
                confidence=85,
            ),
            EvidenceItem(
                source_family="Gamma",
                feature="gamma_wall",
                direction="BULLISH",
                strength=90,
                confidence=95,
            ),
        ]
    )

    assert len(result) == 1
    assert result[0].family == "GAMMA"
    assert result[0].direction == "BULLISH"
    assert result[0].evidence_count == 3
    assert result[0].bullish_count == 3
    assert result[0].bearish_count == 0


def test_conflicting_family_evidence_is_preserved():
    aggregator = FamilyEvidenceAggregator()

    result = aggregator.aggregate(
        [
            EvidenceItem(
                source_family="Gamma",
                feature="GEX",
                direction="BULLISH",
                strength=80,
                confidence=90,
            ),
            EvidenceItem(
                source_family="Gamma",
                feature="gamma_flip",
                direction="BEARISH",
                strength=70,
                confidence=85,
            ),
        ]
    )

    assert len(result) == 1
    assert result[0].family == "GAMMA"
    assert result[0].bullish_count == 1
    assert result[0].bearish_count == 1
    assert result[0].conflict_score > 0


def test_different_families_remain_separate():
    aggregator = FamilyEvidenceAggregator()

    result = aggregator.aggregate(
        [
            EvidenceItem(
                source_family="Gamma",
                feature="GEX",
                direction="BULLISH",
                strength=80,
                confidence=90,
            ),
            EvidenceItem(
                source_family="IV",
                feature="IV Skew",
                direction="BEARISH",
                strength=60,
                confidence=85,
            ),
            EvidenceItem(
                source_family="OI",
                feature="OI Flow",
                direction="BULLISH",
                strength=70,
                confidence=80,
            ),
        ]
    )

    families = {item.family for item in result}

    assert families == {
        "GAMMA",
        "VOLATILITY",
        "OI_FLOW",
    }


def test_family_strength_is_bounded():
    aggregator = FamilyEvidenceAggregator()

    result = aggregator.aggregate(
        [
            EvidenceItem(
                source_family="Gamma",
                feature="GEX",
                direction="BULLISH",
                strength=100,
                confidence=100,
            ),
            EvidenceItem(
                source_family="Gamma",
                feature="gamma_flip",
                direction="BULLISH",
                strength=100,
                confidence=100,
            ),
            EvidenceItem(
                source_family="Gamma",
                feature="gamma_wall",
                direction="BULLISH",
                strength=100,
                confidence=100,
            ),
        ]
    )

    assert 0 <= result[0].strength <= 100
    assert 0 <= result[0].confidence <= 100
    assert 0 <= result[0].freshness <= 100
    assert 0 <= result[0].conflict_score <= 100


def test_unregistered_feature_uses_authoritative_source_family():
    aggregator = FamilyEvidenceAggregator()

    result = aggregator.aggregate(
        [
            EvidenceItem(
                source_family="SCORE",
                feature="probability",
                direction="BEARISH",
                strength=80,
                confidence=55,
            ),
            EvidenceItem(
                source_family="SCORE",
                feature="signal",
                direction="BEARISH",
                strength=55,
                confidence=55,
            ),
        ]
    )

    assert len(result) == 1
    assert result[0].family == "SCORE"
    assert result[0].evidence_count == 2
    assert result[0].bearish_count == 2
