from engine.instrument_manager import InstrumentManager
from engine.strike_selector import StrikeSelector
from engine.market_data_manager import MarketDataManager
from providers.indmoney_provider import INDMoneyProvider

provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()
instrument.load_fno()

market = MarketDataManager(provider)

spot = market.get_spot_price("NIFTY")

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

print("=" * 60)
print("SPOT")
print("=" * 60)
print(spot)

print("\nEXPIRY")
print(expiry)

selector = StrikeSelector(instrument)

contracts = selector.get_option_security_ids(
    symbol="NIFTY",
    expiry=expiry,
    spot_price=spot,
    levels=5
)

print("\n" + "=" * 60)
print("CONTRACTS")
print("=" * 60)

for c in contracts:
    print(c)