from engine.live_engine import LiveEngine

ctx = LiveEngine().build_context()

print()
print("=" * 70)
print(ctx.regime)
print("=" * 70)