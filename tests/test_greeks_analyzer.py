from providers.indmoney_provider import INDMoneyProvider

from engine.instrument_manager import InstrumentManager
from engine.market_data_manager import MarketDataManager
from engine.strike_selector import StrikeSelector
from engine.option_chain_manager import OptionChainManager
from engine.live_greeks_engine import LiveGreeksEngine

from analytics.greeks.greeks_analyzer import GreeksAnalyzer


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

option_chain = greeks.calculate_chain_greeks(
    option_chain,
    spot,
    expiry
)

##################################################
# NEW ANALYZER
##################################################

analyzer = GreeksAnalyzer()

result = analyzer.enrich(
    option_chain,
    spot
)

print("\n")
print("=" * 70)
print("GREEKS ANALYZER")
print("=" * 70)

print(
    result[
        [
            "Strike",
            "CE_GEX",
            "PE_GEX",
            "NET_GEX",
            "NET_DEX",
        ]
    ]
)

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"Spot : {spot}")

print(f"Total GEX : {analyzer.total_gex(result):,.2f}")
print(f"Total DEX : {analyzer.total_dex(result):,.2f}")

print("\nLargest Positive Gamma")

print(
    analyzer.max_gex_strike(result)[
        [
            "Strike",
            "NET_GEX"
        ]
    ]
)

print("\nLargest Negative Gamma")

print(
    analyzer.min_gex_strike(result)[
        [
            "Strike",
            "NET_GEX"
        ]
    ]
)