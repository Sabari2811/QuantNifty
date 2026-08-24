from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd

from core.data_provenance import RuntimeDataProvenance
from engine.market_data_pipeline import MarketDataPipeline


class _Provider:
    def get_historical_data(self, **kwargs):
        return [
            {
                "ts": int(datetime(2026, 8, 24, 10, 0, tzinfo=timezone.utc).timestamp()),
                "o": 100,
                "h": 101,
                "l": 99,
                "c": 100.5,
                "v": 1000,
            },
            {
                "ts": int(datetime(2026, 8, 24, 10, 5, tzinfo=timezone.utc).timestamp()),
                "o": 100.5,
                "h": 102,
                "l": 100,
                "c": 101.5,
                "v": 1200,
            },
        ]


class _Instrument:
    def get_index_security_id(self, symbol):
        return 40000001

    def get_scrip_code(self, segment, security_id):
        return "NIDX_40000001"

    def get_nearest_weekly_expiry(self, symbol):
        return "08/25/2026 14:00"


class _CandleManager:
    def to_dataframe(self, candles):
        return pd.DataFrame(candles)


class _ChainManager:
    def __init__(self, chain):
        self.chain = chain

    def get_live_option_chain(self, symbol, spot, strike_levels):
        return self.chain.copy()


def _pipeline(chain=None):
    return MarketDataPipeline(
        provider=_Provider(),
        instrument=_Instrument(),
        market=None,
        chain_manager=_ChainManager(chain) if chain is not None else None,
        candle_manager=_CandleManager(),
    )


def _valid_chain():
    return pd.DataFrame([
        {
            "Strike": 25000,
            "CE_ID": 111,
            "CE_LTP": 150,
            "CE_OI": 45000,
            "CE_VOLUME": 1200,
            "PE_ID": 222,
            "PE_LTP": 140,
            "PE_OI": 43000,
            "PE_VOLUME": 900,
        }
    ])


def _suspect_chain():
    chain = _valid_chain()
    chain.loc[0, "Strike"] = 24900
    chain.loc[0, "CE_LTP"] = 120
    return chain


def test_provider_candle_timestamp_is_extracted_as_utc():
    pipeline = _pipeline()
    candles = [
        {"ts": 1787565900},
        {"ts": 1787566200},
    ]

    result = pipeline._provider_candle_timestamp(candles)

    assert result == datetime.fromtimestamp(1787566200, tz=timezone.utc)


def test_historical_acquisition_records_provider_timestamp_and_freshness():
    pipeline = _pipeline()
    ctx = SimpleNamespace(
        symbol="NIFTY",
        data_provenance=RuntimeDataProvenance(),
    )

    pipeline._fetch_historical_candles(ctx)

    provenance = ctx.data_provenance.candles
    assert provenance is not None
    assert provenance.provider_timestamp == datetime(
        2026, 8, 24, 10, 5, tzinfo=timezone.utc
    )
    assert provenance.freshness_verified is True
    assert provenance.freshness_seconds is not None
    assert provenance.freshness_seconds >= 0
    assert provenance.reasons == ("provider_candle_timestamp",)


def test_missing_provider_candle_timestamp_is_unverified():
    pipeline = _pipeline()

    assert pipeline._provider_candle_timestamp([{"o": 1, "h": 2}]) is None


def test_live_option_integrity_is_attached_to_runtime_provenance():
    pipeline = _pipeline(_suspect_chain())
    ctx = SimpleNamespace(
        symbol="NIFTY",
        spot=25050.0,
        strike_levels=1,
        data_provenance=RuntimeDataProvenance(
            spot=SimpleNamespace(source="spot")
        ),
    )

    pipeline._fetch_option_chain(ctx)

    provenance = ctx.data_provenance.option_chain
    assert provenance is not None
    assert provenance.integrity_status == "SUSPECT"
    assert "ce_ltp_below_intrinsic" in provenance.integrity_reasons
    assert ctx.option_chain.attrs["quote_integrity"]["status"] == "SUSPECT"


def test_valid_live_option_chain_is_marked_valid_in_runtime_provenance():
    pipeline = _pipeline(_valid_chain())
    ctx = SimpleNamespace(
        symbol="NIFTY",
        spot=25050.0,
        strike_levels=1,
        data_provenance=RuntimeDataProvenance(
            spot=SimpleNamespace(source="spot")
        ),
    )

    pipeline._fetch_option_chain(ctx)

    provenance = ctx.data_provenance.option_chain
    assert provenance is not None
    assert provenance.integrity_status == "VALID"
    assert provenance.integrity_reasons == ()
