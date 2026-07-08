from analytics.greeks.greeks_analyzer import GreeksAnalyzer
from analytics.gamma.gamma_wall import GammaWallDetector

# -------------------------------------------------
# Reuse your existing builder
# -------------------------------------------------

spot_price = ...
option_chain_df = ...

# -------------------------------------------------

analyzer = GreeksAnalyzer()

df = analyzer.enrich(
    option_chain_df,
    spot_price
)

detector = GammaWallDetector()

summary = detector.summary(df)

print()
print("=" * 70)
print("PRIMARY GAMMA WALL")
print("=" * 70)

print(summary["primary_wall"][["Strike", "NET_GEX"]])

print()

print("=" * 70)
print("TOP GAMMA WALLS")
print("=" * 70)

print(
    summary["top_walls"][
        [
            "Strike",
            "NET_GEX"
        ]
    ]
)

print()

print("=" * 70)
print("POSITIVE WALL")
print("=" * 70)

print(summary["positive_wall"][["Strike", "NET_GEX"]])

print()

print("=" * 70)
print("NEGATIVE WALL")
print("=" * 70)

negative = summary["negative_wall"]

if negative is not None:
    print(negative[["Strike", "NET_GEX"]])
else:
    print("No negative gamma wall detected.")