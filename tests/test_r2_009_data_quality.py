from types import SimpleNamespace

from analytics.intelligence.gate import IntelligenceGate
from analytics.intelligence.result import DataQuality
from application.intelligence_service import IntelligenceService


def _item(
    *,
    source="test",
    complete=True,
    expected_count=10,
    received_count=10,
    freshness_verified=True,
    reasons=(),
):
    return SimpleNamespace(
        source=source,
        complete=complete,
        expected_count=expected_count,
        received_count=received_count,
        freshness_verified=freshness_verified,
        reasons=tuple(reasons),
    )


def _context(*items):
    return SimpleNamespace(
        data_provenance=SimpleNamespace(
            spot=items[0] if len(items) > 0 else None,
            option_chain=items[1] if len(items) > 1 else None,
            candles=items[2] if len(items) > 2 else None,
        )
    )


def test_verified_freshness_is_explicitly_verified():
    quality = IntelligenceService._build_data_quality(
        _context(_item(freshness_verified=True))
    )

    assert quality.freshness_verified is True
    assert quality.stale is False
    assert quality.incomplete is False


def test_unverified_freshness_is_not_reported_as_fresh():
    quality = IntelligenceService._build_data_quality(
        _context(_item(freshness_verified=False))
    )

    assert quality.freshness_verified is False
    assert quality.stale is False
    assert "freshness_unverified:test" in quality.reasons


def test_incomplete_acquisition_remains_incomplete():
    quality = IntelligenceService._build_data_quality(
        _context(
            _item(
                complete=False,
                expected_count=10,
                received_count=8,
            )
        )
    )

    assert quality.incomplete is True
    assert quality.score == 80.0


def test_explicit_stale_quality_blocks_execution():
    result = IntelligenceGate().evaluate(
        SimpleNamespace(
            data_quality=DataQuality(
                score=50.0,
                stale=True,
                freshness_verified=True,
            )
        )
    )

    assert result.status == "BLOCK"
    assert "stale" in result.reason.lower()
