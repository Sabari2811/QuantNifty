from decision.market_context import MarketContext
from decision.scoring_engine import ScoringEngine

market = MarketContext()

market.dealer = "LONG"
market.gamma_state = "POSITIVE"
market.pcr_bias = "BULLISH"
market.institutional = "STRONG"
market.probability = 88

score, reasons = ScoringEngine().score(market)

print()
print("=" * 70)
print("Score :", score)
print("Reasons :", reasons)
print("=" * 70)