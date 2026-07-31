from decision.builder import DecisionBuilder
from decision.decision_engine import DecisionEngine
from analytics.market_snapshot.market_snapshot import MarketSnapshot


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

            "score": 76,

            "max_score": 100

        }

    },

    "pcr": {

        "bias": "BULLISH"

    }

}

snapshot = MarketSnapshot().save(

    greeks_df=None,

    spot=24300,

    analytics=analytics

)

ctx = DecisionBuilder().build(snapshot)

decision = DecisionEngine().build(ctx)

print()

print("=" * 70)

print(decision)

print("=" * 70)