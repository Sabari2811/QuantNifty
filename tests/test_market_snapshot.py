from engine.market_snapshot import MarketSnapshot

snapshot = MarketSnapshot()

snapshot.update(
    symbol="NIFTY",
    spot=24270.85,
    expiry="09-Jul-2026"
)

print()

print("=" * 60)
print("MARKET SNAPSHOT")
print("=" * 60)

print(snapshot.to_dict())