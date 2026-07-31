import pandas as pd

from analytics.market_snapshot.market_snapshot import MarketSnapshot
from decision.execution.execution_engine import ExecutionEngine
from decision.models import Decision

df = pd.DataFrame([

    {

        "strike":24400,

        "option_type":"CE",

        "ltp":182.45,

        "delta":0.42,

        "gamma":0.0018,

        "theta":-22,

        "vega":18,

        "iv":12.6,

        "oi":125000,

        "volume":98000

    }

])

snapshot = MarketSnapshot().save(

    greeks_df=df,

    spot=24310,

    analytics={

        "dealer":{

            "call_wall":24400,

            "gamma_wall":24300,

            "put_wall":24100,

            "gamma_flip":24200

        }

    }

)

decision = Decision()

decision.valid = True

decision.signal.name = "BUY CALL"

decision = ExecutionEngine().prepare(

    decision,

    snapshot

)

print()

print("=" * 70)

print(decision.trade)

print("=" * 70)