from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.market_analyzer import MarketAnalyzer

analytics = {

    "dealer": {
        "dealer_gamma": "LONG",
        "gamma_flip": 24200,
        "gamma_wall": 24300,
        "call_wall": 24400,
        "put_wall": 24100
    },

    "prediction": {
        "prediction_score": 88
    },

    "institutional_score": {
        "institutional": {
            "score": 82,
            "max_score": 100
        }
    },

    "pcr": {
        "bias": "BULLISH"
    },

    "expected_move": {
        "expected_move": 185
    },

    "max_pain": {
        "max_pain": 24250
    },

    "atr": {
        "atr": 155
    }

}

snapshot = MarketSnapshot().save(

    greeks_df=None,

    spot=24310,

    analytics=analytics

)

market = MarketAnalyzer().analyze(snapshot)

print()

print("=" * 70)

print(market)

print("=" * 70)