from decision.decision_engine import DecisionEngine
from analytics.market_snapshot.market_snapshot import MarketSnapshot


analytics = {

    "dealer": {

        "dealer_gamma": "LONG"

    },

    "prediction": {

        "prediction_score": 91,

        "move_probability": 84

    },

    "trade_plan": {

        "signal": "BUY",

        "option_type": "CE",

        "recommended_strike": 24200,

        "entry": 180,

        "stop_loss": 130,

        "target1": 260,

        "target2": 330,

        "risk_reward": 2.8,

        "reasons": [

            "Dealer LONG",

            "Above Gamma Flip"

        ]

    },

    "institutional_score": {

        "institutional": {

            "score": 82,

            "max_score": 100

        }

    }

}


snapshot = MarketSnapshot().save(

    greeks_df=None,

    spot=24185,

    analytics=analytics

)

decision = DecisionEngine().build(

    snapshot

)

print()

print("=" * 70)

print(decision)

print("=" * 70)