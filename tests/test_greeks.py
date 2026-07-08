from engine.greeks_engine import GreeksEngine

engine = GreeksEngine()

result = engine.calculate_greeks(
    option_price=132.15,
    spot_price=24270.85,
    strike_price=24200,
    expiry="07/07/2026 14:00",
    option_type="CE"
)

print("\n==========================")
print("OPTION GREEKS")
print("==========================")

for k, v in result.items():
    print(f"{k:10} : {v}")