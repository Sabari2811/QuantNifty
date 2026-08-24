from types import SimpleNamespace

from dashboard.intelligence_adapter import adapt_intelligence


def _result(status):
    quality = SimpleNamespace(
        score=100.0,
        stale=False,
        incomplete=False,
        invalid=False,
        freshness_verified=False,
        reasons=(f"integrity_suspect:options",) if status == "SUSPECT" else (),
    )
    return SimpleNamespace(
        data_quality=quality,
        contract_version="R2-005-A",
        timestamp=None,
        recommendation="WAIT",
        direction="NEUTRAL",
        confidence_before=0.0,
        confidence_after=0.0,
        conviction=0.0,
        opportunity_quality=0.0,
        execution_quality=0.0,
        risk_quality=0.0,
        explanation="",
        regime=SimpleNamespace(
            regime="UNKNOWN",
            previous_regime="UNKNOWN",
            transition=False,
            transition_reason="",
            confidence=0.0,
        ),
        primary_scenario=None,
        alternative_scenario=None,
        invalidation=(),
        reasons=(),
        evidence_summary=SimpleNamespace(
            bullish_count=0,
            bearish_count=0,
            neutral_count=0,
            independent_count=0,
            correlated_count=0,
            confluence_score=0.0,
            conflict_score=0.0,
        ),
        evidence=None,
    )


def test_suspect_integrity_is_not_presented_as_acceptable():
    payload = adapt_intelligence(_result("SUSPECT"))

    assert payload["data_quality"]["status"] == "SUSPECT"
    assert payload["data_quality"]["freshness_status"] == "UNVERIFIED"
    assert "integrity_suspect:options" in payload["data_quality"]["reasons"]


def test_unverified_without_integrity_issue_remains_acceptable():
    payload = adapt_intelligence(_result("UNVERIFIED"))

    assert payload["data_quality"]["status"] == "ACCEPTABLE"
    assert payload["data_quality"]["freshness_status"] == "UNVERIFIED"
