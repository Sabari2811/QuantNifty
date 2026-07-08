from analytics.greeks.greeks_analyzer import GreeksAnalyzer
from analytics.market.market_structure import MarketStructure

# reuse your existing builder

spot_price = ...

option_chain_df = ...

analyzer = GreeksAnalyzer()

df = analyzer.enrich(
    option_chain_df,
    spot_price
)

structure = MarketStructure()

summary = structure.summary(df)

print()

print("=" * 70)
print("MARKET STRUCTURE")
print("=" * 70)

print()

print("Gamma Wall")

print(summary["gamma_wall"][["Strike", "NET_GEX"]])

print()

print("Call Wall")

print(summary["call_wall"][["Strike", "CE_OI"]])

print()

print("Put Wall")

print(summary["put_wall"][["Strike", "PE_OI"]])