from types import SimpleNamespace

from application.intelligence_service import IntelligenceService


def test_resolve_regime_normalizes_market_regime_object():
    runtime_context = SimpleNamespace(
        regime=SimpleNamespace(
            regime="RANGE",
            confidence=42.0,
            transition=False,
        )
    )

    result = IntelligenceService._resolve_regime(runtime_context)

    assert result.regime == "RANGE"
    assert result.confidence == 42.0
    assert result.transition is False


def test_resolve_regime_preserves_unknown_only_when_no_runtime_regime_exists():
    result = IntelligenceService._resolve_regime(SimpleNamespace(regime=None))

    assert result.regime == "UNKNOWN"
    assert result.confidence == 0.0
