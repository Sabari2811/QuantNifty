from analytics.signal.probability_engine import ProbabilityEngine

dealer = {

    "dealer_gamma": "LONG",

    "market_mode": "PINNED"

}

iv_skew = {

    "bias": "CALLS"

}

iv_smile = {

    "shape": "NORMAL"

}

engine = ProbabilityEngine()

result = engine.calculate(
    dealer,
    iv_skew,
    iv_smile
)

print()

print("="*50)

print("Probability Engine")

print("="*50)

print()

for k, v in result.items():

    print(k, ":", v)