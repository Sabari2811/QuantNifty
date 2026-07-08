from analytics.exposure.vanna_exposure_engine import VannaExposureEngine

from engine.live_greeks_engine import LiveGreeksEngine

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.option_chain_manager import OptionChainManager
from engine.strike_selector import StrikeSelector

from providers.indmoney_provider import INDMoneyProvider


provider = INDMoneyProvider()
provider.connect()

instrument = InstrumentManager()
instrument.load_fno()

market = MarketDataManager(provider)

spot = market.get_spot_price("NIFTY")

selector = StrikeSelector(instrument)

chain = OptionChainManager(
    provider,
    selector,
    instrument,
    market
)

expiry = instrument.get_nearest_weekly_expiry("NIFTY")

option_chain = chain.get_live_option_chain(
    "NIFTY",
    spot,
    5
)

greeks = LiveGreeksEngine()

df = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

engine = VannaExposureEngine()

result = engine.calculate(df)

print()

print(result[[
    "Strike",
    "NET_VEX"
]])

print()

print("TOTAL VEX")

print(engine.total_vex(result))