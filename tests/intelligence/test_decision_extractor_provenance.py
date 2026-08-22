from __future__ import annotations

from types import SimpleNamespace

from analytics.intelligence.extractors.decision import DecisionExtractor
from analytics.intelligence.models import TradeIntelligenceRecord


def build_record():
    return TradeIntelligenceRecord()


def build_decision():
    execution = SimpleNamespace(
        trade_quality=87.5,
    )

    trade = SimpleNamespace(
        execution=execution,
    )

    signal = SimpleNamespace(
        name="BUY CALL",
        confidence=82.0,
    )

    return SimpleNamespace(
        signal=signal,
        trade=trade,
        reasons=[
            "Positive dealer gamma",
            "Strong market structure",
        ],
    )


def build_context(decision):
    return SimpleNamespace(
        decision=decision,
    )


# ==========================================================
# Signal provenance
# ==========================================================


def test_signal_comes_from_decision_signal_name():

    decision = build_decision()

    ctx = build_context(decision)

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.signal == "BUY CALL"


# ==========================================================
# Confidence provenance
# ==========================================================


def test_confidence_comes_from_decision_signal_confidence():

    decision = build_decision()

    ctx = build_context(decision)

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.confidence == 82.0


# ==========================================================
# Trade quality provenance
# ==========================================================


def test_trade_quality_comes_from_trade_execution():

    decision = build_decision()

    ctx = build_context(decision)

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.trade_quality == 87.5


# ==========================================================
# Reasons provenance
# ==========================================================


def test_reasons_come_from_decision():

    decision = build_decision()

    ctx = build_context(decision)

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.reasons == [
        "Positive dealer gamma",
        "Strong market structure",
    ]


# ==========================================================
# Object identity / source isolation
# ==========================================================


def test_extractor_does_not_require_legacy_decision_fields():

    decision = build_decision()

    # Deliberately prove that the old, non-authoritative
    # locations are not required.
    assert not hasattr(
        decision,
        "confidence",
    )

    assert not hasattr(
        decision,
        "trade_quality",
    )

    assert not hasattr(
        decision,
        "strategy_name",
    )

    assert not hasattr(
        decision,
        "execution_plan",
    )

    ctx = build_context(decision)

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.signal == "BUY CALL"
    assert record.confidence == 82.0
    assert record.trade_quality == 87.5


# ==========================================================
# Missing decision safety
# ==========================================================


def test_missing_decision_is_safe():

    ctx = SimpleNamespace(
        decision=None,
    )

    record = build_record()

    DecisionExtractor().extract(
        ctx,
        record,
    )

    assert record.signal == ""
    assert record.confidence == 0.0
    assert record.trade_quality == 0.0
    assert record.reasons == []