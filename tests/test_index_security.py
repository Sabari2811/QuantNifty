from engine.instrument_manager import InstrumentManager

im = InstrumentManager()

print(im.get_index_security_id("NIFTY 50"))
print(im.get_index_security_id("BANK NIFTY"))
print(im.get_index_security_id("India VIX"))