from dataclasses import dataclass


@dataclass(frozen=True)
class TradingConfig:
    """
    Central configuration for trading rules.

    Any strategy-level constant should live here instead
    of being hardcoded inside engines.
    """

    # -------------------------------------
    # Capital
    # -------------------------------------

    DEFAULT_CAPITAL = 500000

    DEFAULT_RISK_PERCENT = 1.0

    # -------------------------------------
    # Trade Validation
    # -------------------------------------

    MIN_RISK_REWARD = 1.5

    MIN_OPTION_OI = 50000

    MIN_OPTION_VOLUME = 1000

    # -------------------------------------
    # Premium Targets
    # -------------------------------------

    TARGET1_MULTIPLIER = 1.35

    TARGET2_MULTIPLIER = 1.70

    # -------------------------------------
    # Stop Loss
    # -------------------------------------

    STOPLOSS_LOW_IV = 0.20

    STOPLOSS_NORMAL_IV = 0.25

    STOPLOSS_HIGH_IV = 0.30


    # -------------------------------------
    # IV Thresholds
    # -------------------------------------

    LOW_IV_THRESHOLD = 10

    HIGH_IV_THRESHOLD = 20

    # -------------------------------------
    # Scoring Weights
    # -------------------------------------

    DEALER_LONG_SCORE = 30
    DEALER_SHORT_SCORE = -30

    GAMMA_POSITIVE_SCORE = 20
    GAMMA_NEGATIVE_SCORE = -20

    PCR_BULLISH_SCORE = 15
    PCR_BEARISH_SCORE = -15

    INSTITUTION_STRONG_SCORE = 20
    INSTITUTION_WEAK_SCORE = -20

    PROBABILITY_HIGH_SCORE = 15
    PROBABILITY_LOW_SCORE = -15

    HIGH_PROBABILITY_THRESHOLD = 80
    LOW_PROBABILITY_THRESHOLD = 20