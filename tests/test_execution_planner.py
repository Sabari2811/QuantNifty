from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.execution_planner import ExecutionPlanner
from decision.models import Decision

analytics = {

    "dealer": {

        "call_wall": 24400,

        "put_wall": 24100,

        "gamma_wall": 24350

    },

    "expected_move": {

        "expected_move": 180

    }

}

snapshot = MarketSnapshot().save(

    greeks_df=None,

    spot=24220,

    analytics=analytics

)

decision = Decision()

decision.valid = True

decision.signal.name = "BUY CALL"

planner = ExecutionPlanner()

decision = planner.build(

    decision,

    snapshot

)

print()

print("=" * 70)

print(decision)

print("=" * 70)