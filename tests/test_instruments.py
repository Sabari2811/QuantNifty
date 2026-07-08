from engine.instrument_manager import InstrumentManager

manager = InstrumentManager()

print("=" * 60)
print("FNO COLUMN NAMES")
print("=" * 60)

manager.show_columns("fno")

print("\n")

df = manager.load_instruments("fno")

print("=" * 60)
print("FIRST 10 ROWS")
print("=" * 60)

print(df.head(10))