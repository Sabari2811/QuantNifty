from engine.instrument_manager import InstrumentManager

manager = InstrumentManager()

print("=" * 60)
print("LOOKUP ENGINE TEST")
print("=" * 60)

expiry = manager.get_nearest_weekly_expiry("NIFTY")

print("Nearest Weekly Expiry :", expiry)

print()

option = manager.get_option(
    symbol="NIFTY",
    expiry=expiry,
    strike=24200,
    option_type="CE"
)

print("OPTION CONTRACT")
print("-" * 60)

if option is None:
    print("Option not found")
else:
    print(option)

print()

security_id = manager.get_security_id(
    symbol="NIFTY",
    expiry=expiry,
    strike=24200,
    option_type="CE"
)

print("SECURITY ID :", security_id)

print()

print("LOT SIZE :", manager.get_lot_size("NIFTY"))