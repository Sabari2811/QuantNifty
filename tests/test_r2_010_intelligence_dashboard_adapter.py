from types import SimpleNamespace

from dashboard.intelligence_adapter import adapt_intelligence


def _result(*, freshness_verified=False, stale=False, incomplete=False):
    quality = SimpleNamespace(
        score=100.0,
        freshness_verified=freshness_verified,
        stale=stale,
        incomplete=incomplete,
        invalid=False,
        reasons=("provider_quote_timestamp_unavailable",),
    )

    regime = SimpleNamespace(
        regime="RANGE",
        previous_regime="UNKNOWN",
        transition=False,
        transition_reason="",
        confidence=42.0,
    )

    return SimpleNamespace(
        contract_version="R2-005-A",
        timestamp=None,
        recommendation="WAIT",
        direction="NEUTRAL",
        confidence_before=20.0,
        confidence_after=20.0,
        conviction=0.0,
        opportunity_quality=0.0,
        execution_quality=0.0,
        risk_quality=0.0,
        explanation="test",
        regime=regime,
        primary_scenario=None,
        alternative_scenario=None,
        invalidation=(),
        reasons=(),
        data_quality=quality,
        evidence=SimpleNamespace(
            similar_markets=0,
            average_similarity=0.0,
            best_similarity=0.0,
            win_rate=0.0,
            average_pnl=0.0,
            average_holding_minutes=0.0,
            target_probability=0.0,
            stoploss_probability=0.0,
            breakeven_probability=0.0,
            recommendation="",
            confidence_adjustment=0.0,
            explanation="",
        ),
        evidence_summary=SimpleNamespace(
            bullish_count=0,
            bearish_count=0,
            neutral_count=0,
            independent_count=0,
            correlated_count=0,
            confluence_score=0.0,
            conflict_score=0.0,
        ),
    )


def test_unverified_freshness_is_explicitly_unverified_not_stale():
    payload = adapt_intelligence(_result())

    assert payload["data_quality"]["score"] == 100.0
    assert payload["data_quality"]["status"] == "ACCEPTABLE"
    assert payload["data_quality"]["freshness_status"] == "UNVERIFIED"
    assert payload["data_quality"]["stale"] is False


def test_verified_freshness_is_exposed_as_verified():
    payload = adapt_intelligence(_result(freshness_verified=True))

    assert payload["data_quality"]["freshness_status"] == "VERIFIED"


def test_incomplete_quality_is_not_hidden_by_full_score():
    payload = adapt_intelligence(_result(incomplete=True))

    assert payload["data_quality"]["status"] == "INCOMPLETE"
