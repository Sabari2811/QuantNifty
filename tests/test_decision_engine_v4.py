from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.decision_engine import DecisionEngine


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

import pandas as pd

greeks_df = pd.DataFrame([
    {
        "strike": 24300,
        "option_type": "CE",
        "ltp": 180.0,
        "bid": 179.5,
        "ask": 180.5,
        "volume": 120000,
        "oi": 250000,
        "iv": 14.2,
        "delta": 0.52,
        "gamma": 0.018,
        "theta": -12.5,
        "vega": 8.4,
        "expiry": "31-Jul-2026"
    },
    {
        "strike": 24400,
        "option_type": "CE",
        "ltp": 142.0,
        "bid": 141.5,
        "ask": 142.5,
        "volume": 95000,
        "oi": 180000,
        "iv": 13.9,
        "delta": 0.46,
        "gamma": 0.017,
        "theta": -11.8,
        "vega": 8.1,
        "expiry": "31-Jul-2026"
    },
    {
        "strike": 24200,
        "option_type": "PE",
        "ltp": 165.0,
        "bid": 164.5,
        "ask": 165.5,
        "volume": 110000,
        "oi": 210000,
        "iv": 14.8,
        "delta": -0.48,
        "gamma": 0.019,
        "theta": -13.2,
        "vega": 8.7,
        "expiry": "31-Jul-2026"
    }
])

snapshot = MarketSnapshot().save(
    greeks_df=greeks_df,
    spot=24310,
    analytics=analytics
)

decision = DecisionEngine().build(snapshot)

print()

print("=" * 70)

print(decision)

print("=" * 70)