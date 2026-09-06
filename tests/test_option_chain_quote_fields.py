from engine.option_chain_manager import OptionChainManager


class MockInstrumentManager:
    def get_nearest_weekly_expiry(self, symbol):
        return "07/21/2026 14:00"


class MockStrikeSelector:
    def get_option_security_ids(self, symbol, expiry, spot_price, levels):
        return [{"strike": 25000, "CE_ID": 111, "PE_ID": 222}]


class MockProvider:
    def get_quotes(self, security_ids):
        return {
            "NFO_111": {
                "live_price": 120.5,
                "bid_price": 120.0,
                "ask_price": 121.0,
                "open_interest": 50000,
                "volume": 1200,
            },
            "NFO_222": {
                "live_price": 95.2,
                "bid_price": 95.0,
                "ask_price": 95.5,
                "open_interest": 47000,
                "volume": 900,
            },
        }


def test_option_chain_preserves_provider_bid_ask_without_synthesis():
    manager = OptionChainManager(
        provider=MockProvider(),
        strike_selector=MockStrikeSelector(),
        instrument_manager=MockInstrumentManager(),
        market_manager=None,
    )

    df = manager.get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=1,
    )

    row = df.iloc[0]
    assert row["CE_LTP"] == 120.5
    assert row["CE_BID"] == 120.0
    assert row["CE_ASK"] == 121.0
    assert row["PE_LTP"] == 95.2
    assert row["PE_BID"] == 95.0
    assert row["PE_ASK"] == 95.5


def test_option_chain_keeps_missing_bid_ask_as_unknown():
    class MissingQuoteProvider(MockProvider):
        def get_quotes(self, security_ids):
            quotes = super().get_quotes(security_ids)
            quotes["NFO_111"].pop("bid_price")
            quotes["NFO_111"].pop("ask_price")
            return quotes

    manager = OptionChainManager(
        provider=MissingQuoteProvider(),
        strike_selector=MockStrikeSelector(),
        instrument_manager=MockInstrumentManager(),
        market_manager=None,
    )

    df = manager.get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=1,
    )

    row = df.iloc[0]
    assert row["CE_BID"] is None
    assert row["CE_ASK"] is None
    assert row["PE_BID"] == 95.0
    assert row["PE_ASK"] == 95.5
