from providers.indmoney_provider import INDMoneyProvider
from engine.market_data_manager import MarketDataManager
from engine.instrument_manager import InstrumentManager

provider = INDMoneyProvider()
provider.connect()

manager = InstrumentManager()

expiry = manager.get_nearest_weekly_expiry("NIFTY")

security_id = manager.get_security_id(
    symbol="NIFTY",
    expiry=expiry,
    strike=24200,
    option_type="CE"
)

market = MarketDataManager(provider)

quote = market.get_quote(security_id)

print("\n==============================")
print("LIVE OPTION DATA")
print("==============================")

for key, value in quote.items():
    print(f"{key:15} : {value}")