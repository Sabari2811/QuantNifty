import pandas as pd

from engine.option_chain_manager import OptionChainManager


class _Provider:
    def get_quotes(self, security_ids):
        return {
            "NFO_101": {
                "live_price": 100,
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


def test_live_option_chain_attaches_integrity_without_changing_raw_values():
    manager = OptionChainManager(
        provider=_Provider(),
        strike_selector=_Selector(),
        instrument_manager=_Instrument(),
        market_manager=_Market(),
    )

    result = manager.get_live_option_chain(
        symbol="NIFTY",
        spot_price=25050,
        levels=1,
    )

    assert isinstance(result, pd.DataFrame)
    assert result.loc[0, "CE_LTP"] == 100
    assert result.loc[0, "PE_LTP"] == 150

    provenance = result.attrs["data_provenance"]
    integrity = result.attrs["quote_integrity"]

    assert provenance.integrity_status == "SUSPECT"
    assert "ce_ltp_below_intrinsic" in provenance.integrity_reasons
    assert integrity["status"] == "SUSPECT"
    assert integrity["suspect_contracts"] == 1
