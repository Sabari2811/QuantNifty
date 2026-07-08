from engine.instrument_manager import InstrumentManager

im = InstrumentManager()

im.load_fno()

print(im.__dict__.keys())