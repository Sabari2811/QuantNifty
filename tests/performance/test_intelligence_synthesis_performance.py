from __future__ import annotations

from time import perf_counter

from decision.models import Decision
from decision.models.option_contract import OptionContract

from analytics.intelligence.synthesis.family_aggregator import (
    FamilyEvidence,
)
from analytics.intelligence.synthesis.orchestration.engine import (
    IntelligenceSynthesisEngine,
)


def build_decision():
    decision = Decision()

    decision.trade.risk_reward = 2.0

    decision.trade.contract = OptionContract(
        strike=24400,
        option_type="CE",
        ltp=182.45,
        iv=12.6,
        oi=125000,
        volume=98000,
        delta=0.42,
    )

    return decision


def build_families():
    return [
        FamilyEvidence(
            family="GAMMA",
            direction="BULLISH",
            strength=80.0,
            confidence=90.0,
            freshness=100.0,
        ),
        FamilyEvidence(
            family="STRUCTURE",
            direction="BULLISH",
            strength=75.0,
            confidence=85.0,
            freshness=100.0,
        ),
        FamilyEvidence(
            family="OI_FLOW",
            direction="BEARISH",
            strength=40.0,
            confidence=70.0,
            freshness=100.0,
        ),
    ]


def test_intelligence_synthesis_performance_baseline():
    engine = IntelligenceSynthesisEngine()

    decision = build_decision()
    families = build_families()

    # Warm-up: avoid measuring first-call initialization.
    engine.synthesize(
        families=families,
        decision=decision,
        regime="TRENDING_UP",
        regime_confidence=90.0,
        transition=False,
    )

    iterations = 100

    start = perf_counter()

    for _ in range(iterations):
        result = engine.synthesize(
            families=families,
            decision=decision,
            regime="TRENDING_UP",
            regime_confidence=90.0,
            transition=False,
        )

        assert result is not None

    elapsed = perf_counter() - start

    average_ms = (
        elapsed / iterations
    ) * 1000

    print()
    print("=" * 70)
    print("INTELLIGENCE SYNTHESIS PERFORMANCE")
    print("=" * 70)
    print(f"Iterations       : {iterations}")
    print(f"Total time       : {elapsed:.4f}s")
    print(f"Average / run    : {average_ms:.4f}ms")
    print("=" * 70)

    # This is intentionally informational rather than a hard
    # machine-dependent performance threshold.
    assert elapsed >= 0.0