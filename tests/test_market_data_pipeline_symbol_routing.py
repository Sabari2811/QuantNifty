from datetime import datetime

import pandas as pd

from engine.market_data_pipeline import MarketDataPipeline


class FakeInstrument:
    def __init__(self):
        self.requested_symbol = None

    def get_index_security_id(self, symbol):
        self.requested_symbol = symbol
        return {"BANK NIFTY": 123456, "NIFTY 50": 40000001}[symbol]

    def get_scrip_code(self, exchange, security_id):
        return f"{exchange}_{security_id}"


class FakeProvider:
    def __init__(self):
        self.requested_scrip_code = None

    def get_historical_data(self, **kwargs):
        self.requested_scrip_code = kwargs["scrip_code"]
        return []


class FakeMarket:
    def get_spot_price(self, symbol):
        return 50000.0


class FakeChainManager:
    def get_live_option_chain(self, symbol, spot, strikes):
        return pd.DataFrame()


class FakeCandleManager:
    def to_dataframe(self, candles):
        return pd.DataFrame()


class FakeContext:
    symbol = "BANK NIFTY"
    spot = None
    expiry = None
    option_chain = None
    candles = None


def test_historical_candles_use_active_context_symbol():
    instrument = FakeInstrument()
    provider = FakeProvider()

    pipeline = MarketDataPipeline(
        provider=provider,
        instrument=instrument,
        market=FakeMarket(),
        chain_manager=FakeChainManager(),
        candle_manager=FakeCandleManager(),
    )

    pipeline._fetch_historical_candles(FakeContext())

    assert instrument.requested_symbol == "BANK NIFTY"
    assert provider.requested_scrip_code == "NIDX_123456"


def test_historical_candles_preserve_nifty_symbol_routing():
    instrument = FakeInstrument()
    provider = FakeProvider()

    pipeline = MarketDataPipeline(
        provider=provider,
        instrument=instrument,
        market=FakeMarket(),
        chain_manager=FakeChainManager(),
        candle_manager=FakeCandleManager(),
    )

    context = FakeContext()
    context.symbol = "NIFTY 50"

    pipeline._fetch_historical_candles(context)

    assert instrument.requested_symbol == "NIFTY 50"
    assert provider.requested_scrip_code == "NIDX_40000001"
