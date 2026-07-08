from analytics.oi.oi_flow_engine import OIFlowEngine

import pandas as pd

df = pd.DataFrame({

    "Strike":[24000,24050,24100],

    "CE_LTP":[100,80,60],
    "CE_OI":[10000,9000,7000],

    "PE_LTP":[10,20,40],
    "PE_OI":[5000,7000,9000]

})

engine = OIFlowEngine()

result = engine.analyze(df)

print()

print(result[
    [
        "Strike",
        "CE_FLOW",
        "PE_FLOW"
    ]
])