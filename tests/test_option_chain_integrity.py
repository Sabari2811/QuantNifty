import pandas as pd

from engine.option_chain_manager import OptionChainManager


class _Provider:
    def get_quotes(self, security_ids):
        return {
            "NFO_101": {
                "live_price": 90,
                "open_interest": 1000,
                "volume": 100,
            },
            "NFO_102": {
                "live_price": 150,
                "open_interest": 1200,
                "volume": 200,
            },
        }


class _Selector:
    def get_option_security_ids(self, **kwargs):
        return [{"strike": 24950, "CE_ID": 101, "PE_ID": 102}]


class _Instrument:
    def get_nearest_weekly_expiry(self, symbol):
        return "25/08/2026 14:00"


class _Market:
    pass


def _manager(provider=None, selector=None):
    return OptionChainManager(
        provider=provider or _Provider(),
        strike_selector=selector or _Selector(),
        instrument_manager=_Instrument(),
        market_manager=_Market(),
    )


def test_live_option_chain_attaches_integrity_without_changing_raw_values():
    result = _manager().get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=1,
    )

    assert isinstance(result, pd.DataFrame)
    assert result.loc[0, "CE_LTP"] == 90
    assert result.loc[0, "PE_LTP"] == 150

    provenance = result.attrs["data_provenance"]
    integrity = result.attrs["quote_integrity"]

    assert provenance.integrity_status == "SUSPECT"
    assert "ce_ltp_below_intrinsic" in provenance.integrity_reasons
    assert integrity["status"] == "SUSPECT"
    assert integrity["suspect_contracts"] == 1


def test_missing_provider_contract_is_partial_and_invalid_not_silently_complete():
    class _PartialProvider(_Provider):
        def get_quotes(self, security_ids):
            quotes = super().get_quotes(security_ids)
            quotes.pop("NFO_102")
            return quotes

    result = _manager(provider=_PartialProvider()).get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=0,
    )

    provenance = result.attrs["data_provenance"]

    assert provenance.expected_count == 2
    assert provenance.received_count == 1
    assert provenance.missing_count == 1
    assert provenance.coverage_status == "PARTIAL"
    assert provenance.complete is False
    assert provenance.integrity_status == "INVALID"
    assert "missing_provider_quotes:1" in provenance.reasons
    assert "missing_pe_ltp" in provenance.integrity_reasons
    assert result.loc[0, "PE_LTP"] is None


def test_empty_provider_response_is_empty_and_invalid():
    class _EmptyProvider:
        def get_quotes(self, security_ids):
            return {}

    result = _manager(provider=_EmptyProvider()).get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=0,
    )

    provenance = result.attrs["data_provenance"]

    assert provenance.expected_count == 2
    assert provenance.received_count == 0
    assert provenance.missing_count == 2
    assert provenance.coverage_status == "EMPTY"
    assert provenance.complete is False
    assert provenance.integrity_status == "INVALID"
    assert "missing_provider_quotes:2" in provenance.reasons
    assert "missing_ce_ltp" in provenance.integrity_reasons
    assert "missing_pe_ltp" in provenance.integrity_reasons


def test_selector_under_delivery_preserves_expected_denominator():
    class _UnderSelector:
        def get_option_security_ids(self, **kwargs):
            return [{"strike": 24950, "CE_ID": 101, "PE_ID": 102}]

    result = _manager(selector=_UnderSelector()).get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=2,
    )

    provenance = result.attrs["data_provenance"]

    assert provenance.expected_count == 10
    assert provenance.received_count == 2
    assert provenance.missing_count == 8
    assert provenance.coverage_status == "PARTIAL"
    assert provenance.complete is False
    assert "missing_instrument_contracts:8" in provenance.reasons


def test_degraded_chain_is_not_analytics_complete():
    class _PartialProvider(_Provider):
        def get_quotes(self, security_ids):
            return {"NFO_101": super().get_quotes(security_ids)["NFO_101"]}

    result = _manager(provider=_PartialProvider()).get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=0,
    )

    provenance = result.attrs["data_provenance"]
    integrity = result.attrs["quote_integrity"]

    assert provenance.complete is False
    assert provenance.coverage_status == "PARTIAL"
    assert integrity["status"] == "INVALID"
    assert result.attrs["data_provenance"].status == "INVALID"
