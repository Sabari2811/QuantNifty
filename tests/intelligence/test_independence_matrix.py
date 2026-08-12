from analytics.intelligence.synthesis.independence import (
    EvidenceIndependenceMatrix,
)


def test_gamma_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("GEX").name == "GAMMA"
    assert matrix.classify("gamma_flip").name == "GAMMA"
    assert matrix.classify("gamma_wall").name == "GAMMA"


def test_volatility_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("IV").name == "VOLATILITY"
    assert matrix.classify("IV Skew").name == "VOLATILITY"
    assert matrix.classify("IV Rank").name == "VOLATILITY"


def test_oi_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("OI").name == "OI_FLOW"
    assert matrix.classify("OI Flow").name == "OI_FLOW"
    assert matrix.classify("open_interest").name == "OI_FLOW"


def test_dealer_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("DEX").name == "DEALER"
    assert matrix.classify("Vanna").name == "DEALER"
    assert matrix.classify("Charm").name == "DEALER"


def test_technical_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("VWAP").name == "TECHNICAL"
    assert matrix.classify("RSI").name == "TECHNICAL"
    assert matrix.classify("MACD").name == "TECHNICAL"


def test_score_and_historical_family():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify("institutional_score").name == "SCORE"
    assert matrix.classify("historical_similarity").name == "HISTORICAL"


def test_unknown_feature_is_other():
    matrix = EvidenceIndependenceMatrix()

    result = matrix.classify("completely_unknown_signal")

    assert result.name == "OTHER"
    assert result.aliases == ("completely_unknown_signal",)


def test_feature_normalization():
    matrix = EvidenceIndependenceMatrix()

    assert matrix.classify(" Gamma-Flip ").name == "GAMMA"
    assert matrix.classify("IV Skew").name == "VOLATILITY"
    assert matrix.classify("OI Flow").name == "OI_FLOW"