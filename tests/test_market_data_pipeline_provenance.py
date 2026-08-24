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


class _CandleManager:
    def to_dataframe(self, candles):
        return pd.DataFrame(candles)


def _pipeline():
    return MarketDataPipeline(
        provider=_Provider(),
        instrument=_Instrument(),
        market=None,
        chain_manager=None,
        candle_manager=_CandleManager(),
    )


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
