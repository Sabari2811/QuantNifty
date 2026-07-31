from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.market_regime_engine import MarketRegimeEngine

analytics = {

    "dealer": {

        "dealer_gamma": "LONG"

    },

    "prediction": {

        "prediction_score": 88

    },

    "pcr": {

        "bias": "BULLISH"

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

regime = MarketRegimeEngine().analyze(snapshot)

print()

print("=" * 70)

print(regime)

print("=" * 70)