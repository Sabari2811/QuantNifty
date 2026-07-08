from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine


provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()
instrument.load_fno()

market = MarketDataManager(provider)

selector = StrikeSelector(instrument)

chain = OptionChainManager(
    provider,
    selector,
    instrument,
    market
)

spot = 24270.85

option_chain = chain.get_live_option_chain(
    symbol="NIFTY",
    spot_price=spot,
    levels=5
)

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

greeks = LiveGreeksEngine()

result = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

print("\n==========================")
print("LIVE GREEKS")
print("==========================")

print(result)