from __future__ import annotations

from dataclasses import replace

import pytest

from analytics.intelligence.gate import IntelligenceGate
from analytics.intelligence.gate_models import (
    IntelligenceGateResult,
)
from analytics.intelligence.result import (
    DataQuality,
    IntelligenceResult,
)


# ==========================================================
# Fixtures
# ==========================================================


def build_intelligence_result() -> IntelligenceResult:
    """
    Build a minimal valid IntelligenceResult.

    The gate must only depend on the fields that it owns.
    """

    return IntelligenceResult(
        record=object(),
        evidence=object(),
        recommendation="WAIT",
        confidence_before=70.0,
        confidence_after=70.0,
        explanation="Test intelligence result.",
    )


# ==========================================================
# Result model
# ==========================================================


def test_gate_result_allow():

    result = IntelligenceGateResult(
        status="ALLOW",
        reason="Allowed.",
    )

    assert result.status == "ALLOW"

    assert result.allowed is True

    assert result.blocked is False


def test_gate_result_block():

    result = IntelligenceGateResult(
        status="BLOCK",
        reason="Blocked.",
        reasons=("Blocked.",),
    )

    assert result.status == "BLOCK"

    assert result.allowed is False

    assert result.blocked is True


# ==========================================================
# Default policy
# ==========================================================


def test_gate_allows_valid_intelligence():

    intelligence = build_intelligence_result()

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.allowed is True

    assert result.blocked is False

    assert result.status == "ALLOW"


# ==========================================================
# Data quality gates
# ==========================================================


def test_gate_blocks_invalid_data():

    intelligence = build_intelligence_result()

    intelligence = replace(
        intelligence,
        data_quality=DataQuality(
            score=0.0,
            invalid=True,
            reasons=("Invalid source data.",),
        ),
    )

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.status == "BLOCK"

    assert result.blocked is True

    assert (
        "invalid"
        in result.reason.lower()
    )


def test_gate_blocks_stale_data():

    intelligence = build_intelligence_result()

    intelligence = replace(
        intelligence,
        data_quality=DataQuality(
            score=50.0,
            stale=True,
            reasons=("Stale market data.",),
        ),
    )

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.status == "BLOCK"

    assert (
        "stale"
        in result.reason.lower()
    )


def test_gate_blocks_incomplete_data():

    intelligence = build_intelligence_result()

    intelligence = replace(
        intelligence,
        data_quality=DataQuality(
            score=50.0,
            incomplete=True,
            reasons=("Incomplete market data.",),
        ),
    )

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.status == "BLOCK"

    assert (
        "incomplete"
        in result.reason.lower()
    )


# ==========================================================
# Multiple failures
# ==========================================================


def test_gate_reports_all_data_quality_failures():

    intelligence = build_intelligence_result()

    intelligence = replace(
        intelligence,
        data_quality=DataQuality(
            score=0.0,
            stale=True,
            incomplete=True,
            invalid=True,
            reasons=(
                "Invalid.",
                "Stale.",
                "Incomplete.",
            ),
        ),
    )

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.status == "BLOCK"

    assert len(result.reasons) == 3

    assert (
        "invalid"
        in result.reasons[0].lower()
    )

    assert (
        "stale"
        in result.reasons[1].lower()
    )

    assert (
        "incomplete"
        in result.reasons[2].lower()
    )


# ==========================================================
# No strategy threshold invention
# ==========================================================


@pytest.mark.parametrize(
    "conviction,opportunity_quality,risk_quality",
    [
        (0.0, 0.0, 0.0),
        (10.0, 20.0, 30.0),
        (50.0, 50.0, 50.0),
        (100.0, 100.0, 100.0),
    ],
)
def test_gate_does_not_invent_quality_thresholds(
    conviction,
    opportunity_quality,
    risk_quality,
):

    intelligence = replace(
        build_intelligence_result(),
        conviction=conviction,
        opportunity_quality=opportunity_quality,
        risk_quality=risk_quality,
    )

    result = IntelligenceGate().evaluate(
        intelligence
    )

    assert result.status == "ALLOW"


# ==========================================================
# Required Intelligence object
# ==========================================================


def test_gate_requires_intelligence_result():

    with pytest.raises(ValueError):

        IntelligenceGate().evaluate(
            None
        )