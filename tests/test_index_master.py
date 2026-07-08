from engine.instrument_manager import InstrumentManager

im = InstrumentManager()

df = im.load_index()

print(df.columns)

print()

print(df.head(20))