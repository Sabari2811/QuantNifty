import pandas as pd

from engine.option_chain_manager import OptionChainManager


class MockInstrumentManager:
    def get_nearest_weekly_expiry(self, symbol):
        return "09/01/2026 14:00"


class MockStrikeSelector:
    def __init__(self, contracts):
        self.contracts = contracts

    def get_option_security_ids(self, symbol, expiry, spot_price, levels):
        return list(self.contracts)


class MockProvider:
    def __init__(self, quotes):
        self.quotes = quotes

    def get_quotes(self, security_ids):
        return {
            f"NFO_{sid}": self.quotes[sid]
            for sid in security_ids
            if sid in self.quotes
        }


def _quote(ltp=100, oi=1000, volume=100):
    return {
        "live_price": ltp,
        "open_interest": oi,
        "volume": volume,
    }


def _manager(contracts, quotes):
    return OptionChainManager(
        provider=MockProvider(quotes),
        strike_selector=MockStrikeSelector(contracts),
        instrument_manager=MockInstrumentManager(),
        market_manager=None,
    )


def test_full_option_chain_coverage_is_complete():
    contracts = [
        {"strike": 25000, "CE_ID": 111, "PE_ID": 112},
        {"strike": 25050, "CE_ID": 113, "PE_ID": 114},
        {"strike": 25100, "CE_ID": 115, "PE_ID": 116},
    ]
    quotes = {sid: _quote() for sid in range(111, 117)}

    chain = _manager(contracts, quotes).get_live_option_chain(
        "NIFTY", 25025, levels=1
    )
    provenance = chain.attrs["data_provenance"]

    assert provenance.expected_count == 6
    assert provenance.received_count == 6
    assert provenance.missing_count == 0
    assert provenance.coverage_status == "COMPLETE"
    assert provenance.coverage_ratio == 100.0


def test_missing_instrument_contracts_reduce_coverage():
    contracts = [
        {"strike": 25000, "CE_ID": 111, "PE_ID": 112},
        {"strike": 25100, "CE_ID": 115, "PE_ID": 116},
    ]
    quotes = {sid: _quote() for sid in (111, 112, 115, 116)}

    chain = _manager(contracts, quotes).get_live_option_chain(
        "NIFTY", 25050, levels=1
    )
    provenance = chain.attrs["data_provenance"]

    assert provenance.expected_count == 6
    assert provenance.received_count == 4
    assert provenance.missing_count == 2
    assert provenance.coverage_status == "PARTIAL"
    assert provenance.coverage_ratio == (4 / 6) * 100
    assert "missing_instrument_contracts:2" in provenance.reasons


def test_missing_provider_quotes_reduce_coverage():
    contracts = [
        {"strike": 25000, "CE_ID": 111, "PE_ID": 112},
        {"strike": 25050, "CE_ID": 113, "PE_ID": 114},
        {"strike": 25100, "CE_ID": 115, "PE_ID": 116},
    ]
    quotes = {
        111: _quote(),
        112: _quote(),
        113: _quote(),
        114: _quote(),
        115: _quote(),
    }

    chain = _manager(contracts, quotes).get_live_option_chain(
        "NIFTY", 25025, levels=1
    )
    provenance = chain.attrs["data_provenance"]

    assert provenance.expected_count == 6
    assert provenance.received_count == 5
    assert provenance.missing_count == 1
    assert provenance.coverage_status == "PARTIAL"
    assert "missing_provider_quotes:1" in provenance.reasons
    assert pd.isna(chain.iloc[2]["PE_LTP"])
