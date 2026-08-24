from __future__ import annotations

from analytics.intelligence.result import (
    EvidenceSummary,
    IntelligenceResult,
)
from analytics.intelligence.evidence.models import HistoricalEvidence


def _scenario_payload(scenario):
    if scenario is None:
        return None

    return {
        "name": scenario.name,
        "direction": scenario.direction,
        "probability": scenario.probability,
        "trigger": scenario.trigger,
        "invalidation": scenario.invalidation,
        "rationale": scenario.rationale,
    }


def adapt_intelligence(result: IntelligenceResult | None) -> dict | None:
    """Adapt the canonical IntelligenceResult into a UI-safe dictionary.

    This adapter is observational only. It does not recalculate scores,
    change execution policy, or infer freshness from acquisition time.

    Legacy/test doubles may omit newer R2-005 fields. Missing optional
    presentation data is represented as an empty payload; no intelligence,
    freshness, or quality values are inferred.
    """

    if result is None:
        return None

    quality = result.data_quality

    if quality.invalid:
        quality_status = "INVALID"
    elif quality.stale:
        quality_status = "STALE"
    elif quality.incomplete:
        quality_status = "INCOMPLETE"
    else:
        quality_status = "ACCEPTABLE"

    # Missing provenance must remain UNVERIFIED; never infer freshness from
    # acquisition time or from the quality score.
    freshness_verified = getattr(quality, "freshness_verified", False)
    freshness_status = "VERIFIED" if freshness_verified else "UNVERIFIED"

    evidence = getattr(result, "evidence", None) or HistoricalEvidence()
    summary = getattr(result, "evidence_summary", None) or EvidenceSummary()

    return {
        "contract_version": result.contract_version,
        "timestamp": result.timestamp,
        "recommendation": result.recommendation,
        "direction": result.direction,
        "confidence_before": result.confidence_before,
        "confidence_after": result.confidence_after,
        "conviction": result.conviction,
        "opportunity_quality": result.opportunity_quality,
        "execution_quality": result.execution_quality,
        "risk_quality": result.risk_quality,
        "explanation": result.explanation,
        "regime": {
            "regime": result.regime.regime,
            "previous_regime": result.regime.previous_regime,
            "transition": result.regime.transition,
            "transition_reason": result.regime.transition_reason,
            "confidence": result.regime.confidence,
        },
        "primary_scenario": _scenario_payload(result.primary_scenario),
        "alternative_scenario": _scenario_payload(result.alternative_scenario),
        "invalidation": result.invalidation,
        "reasons": result.reasons,
        "evidence_summary": {
            "bullish_count": summary.bullish_count,
            "bearish_count": summary.bearish_count,
            "neutral_count": summary.neutral_count,
            "independent_count": summary.independent_count,
            "correlated_count": summary.correlated_count,
            "confluence_score": summary.confluence_score,
            "conflict_score": summary.conflict_score,
        },
        "historical_evidence": {
            "similar_markets": evidence.similar_markets,
            "average_similarity": evidence.average_similarity,
            "best_similarity": evidence.best_similarity,
            "win_rate": evidence.win_rate,
            "average_pnl": evidence.average_pnl,
            "average_holding_minutes": evidence.average_holding_minutes,
            "target_probability": evidence.target_probability,
            "stoploss_probability": evidence.stoploss_probability,
            "breakeven_probability": evidence.breakeven_probability,
            "recommendation": evidence.recommendation,
            "confidence_adjustment": evidence.confidence_adjustment,
            "explanation": evidence.explanation,
        },
        "data_quality": {
            "score": quality.score,
            "status": quality_status,
            "freshness_status": freshness_status,
            "freshness_verified": freshness_verified,
            "stale": quality.stale,
            "incomplete": quality.incomplete,
            "invalid": quality.invalid,
            "reasons": quality.reasons,
        },
    }
