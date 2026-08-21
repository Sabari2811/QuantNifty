from __future__ import annotations

import pandas as pd
import pytest

from analytics.gamma.gamma_flip import GammaFlipDetector


# ==========================================================
# Helpers
# ==========================================================

def make_df(gammas, strikes=None):
    if strikes is None:
        strikes = [
            24000 + (index * 50)
            for index in range(len(gammas))
        ]

    return pd.DataFrame(
        {
            "Strike": strikes,
            "NET_GEX": gammas,
        }
    )


# ==========================================================
# Fixture
# ==========================================================

@pytest.fixture
def detector():
    return GammaFlipDetector()


# ==========================================================
# Positive → Negative
# ==========================================================

def test_positive_to_negative_flip(detector):

    df = make_df(
        [100.0, 50.0, -25.0],
        [24000, 24050, 24100],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "POSITIVE_TO_NEGATIVE"
    )

    assert result["lower_strike"] == 24050
    assert result["upper_strike"] == 24100
    assert result["gamma_flip"] == 24100


# ==========================================================
# Negative → Positive
# ==========================================================

def test_negative_to_positive_flip(detector):

    df = make_df(
        [-100.0, -50.0, 25.0],
        [24000, 24050, 24100],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "NEGATIVE_TO_POSITIVE"
    )

    assert result["lower_strike"] == 24050
    assert result["upper_strike"] == 24100
    assert result["gamma_flip"] == 24100


# ==========================================================
# Negative → Zero
# ==========================================================

def test_negative_to_zero_is_negative_to_positive_flip(
    detector,
):

    df = make_df(
        [-100.0, 0.0],
        [24000, 24050],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "NEGATIVE_TO_POSITIVE"
    )

    assert result["lower_strike"] == 24000
    assert result["upper_strike"] == 24050
    assert result["gamma_flip"] == 24050


# ==========================================================
# Positive → Zero
# ==========================================================

def test_positive_to_zero_is_positive_to_negative_flip(
    detector,
):

    df = make_df(
        [100.0, 0.0],
        [24000, 24050],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "POSITIVE_TO_NEGATIVE"
    )

    assert result["lower_strike"] == 24000
    assert result["upper_strike"] == 24050
    assert result["gamma_flip"] == 24050


# ==========================================================
# No flip
# ==========================================================

def test_no_flip_when_gamma_remains_positive(detector):

    df = make_df(
        [10.0, 20.0, 30.0],
        [24000, 24050, 24100],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None
    assert result["lower_strike"] is None
    assert result["upper_strike"] is None


def test_no_flip_when_gamma_remains_negative(detector):

    df = make_df(
        [-10.0, -20.0, -30.0],
        [24000, 24050, 24100],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None
    assert result["lower_strike"] is None
    assert result["upper_strike"] is None


# ==========================================================
# Zero without crossing
# ==========================================================

def test_zero_to_positive_does_not_create_flip(detector):

    df = make_df(
        [0.0, 100.0],
        [24000, 24050],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None


def test_zero_to_negative_does_not_create_flip(detector):

    df = make_df(
        [0.0, -100.0],
        [24000, 24050],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None


# ==========================================================
# First crossing in a longer sequence
# ==========================================================

def test_first_gamma_flip_is_returned(detector):

    df = make_df(
        [-100.0, -50.0, 25.0, 100.0, -20.0],
        [24000, 24050, 24100, 24150, 24200],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "NEGATIVE_TO_POSITIVE"
    )

    assert result["lower_strike"] == 24050
    assert result["upper_strike"] == 24100
    assert result["gamma_flip"] == 24100


# ==========================================================
# Single row
# ==========================================================

def test_single_row_has_no_flip(detector):

    df = make_df(
        [100.0],
        [24000],
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None
    assert result["lower_strike"] is None
    assert result["upper_strike"] is None


# ==========================================================
# Empty DataFrame
# ==========================================================

def test_empty_dataframe_has_no_flip(detector):

    df = pd.DataFrame(
        columns=[
            "Strike",
            "NET_GEX",
        ]
    )

    result = detector.analyze(df)

    assert result["flip_found"] is False
    assert result["direction"] is None
    assert result["lower_strike"] is None
    assert result["upper_strike"] is None


# ==========================================================
# Missing NET_GEX
# ==========================================================

def test_missing_net_gex_raises_value_error(detector):

    df = pd.DataFrame(
        {
            "Strike": [24000, 24050],
            "GEX": [-100.0, 100.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="NET_GEX column not found",
    ):
        detector.analyze(df)


# ==========================================================
# Backward compatibility: detect()
# ==========================================================

def test_detect_delegates_to_analyze(detector):

    df = make_df(
        [-100.0, 100.0],
        [24000, 24050],
    )

    result = detector.detect(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "NEGATIVE_TO_POSITIVE"
    )

    assert result["gamma_flip"] == 24050


# ==========================================================
# Backward compatibility: find_flip()
# ==========================================================

def test_find_flip_delegates_to_analyze(detector):

    df = make_df(
        [100.0, -100.0],
        [24000, 24050],
    )

    result = detector.find_flip(df)

    assert result["flip_found"] is True

    assert (
        result["direction"]
        == "POSITIVE_TO_NEGATIVE"
    )

    assert result["gamma_flip"] == 24050