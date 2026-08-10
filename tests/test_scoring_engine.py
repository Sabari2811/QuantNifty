from decision.market_context import MarketContext
from decision.scoring_engine import ScoringEngine
from config.trading_config import TradingConfig


def test_scoring_engine_returns_score_reasons_and_breakdown():
    market = MarketContext()
    market.dealer = "LONG"
    market.gamma_state = "POSITIVE"
    market.pcr_bias = "BULLISH"
    market.institutional = "STRONG"
    market.probability = 88

    result = ScoringEngine().score(market)

    expected_score = (
        TradingConfig.DEALER_LONG_SCORE
        + TradingConfig.GAMMA_POSITIVE_SCORE
        + TradingConfig.PCR_BULLISH_SCORE
        + TradingConfig.INSTITUTION_STRONG_SCORE
        + TradingConfig.PROBABILITY_HIGH_SCORE
    )

    assert isinstance(result, dict)
    assert set(result) == {"score", "reasons", "breakdown"}
    assert result["score"] == expected_score
    assert result["breakdown"]["total"] == expected_score
    assert result["breakdown"]["dealer"] == TradingConfig.DEALER_LONG_SCORE
    assert result["breakdown"]["gamma"] == TradingConfig.GAMMA_POSITIVE_SCORE
    assert result["breakdown"]["pcr"] == TradingConfig.PCR_BULLISH_SCORE
    assert result["breakdown"]["institutional"] == TradingConfig.INSTITUTION_STRONG_SCORE
    assert result["breakdown"]["probability"] == TradingConfig.PROBABILITY_HIGH_SCORE
    assert "Dealer LONG" in result["reasons"]
    assert "Positive Gamma" in result["reasons"]
    assert "PCR Bullish" in result["reasons"]
    assert "Institution Buying" in result["reasons"]
    assert "High Probability" in result["reasons"]
