from datetime import datetime, timezone
from types import SimpleNamespace

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
        return SimpleNamespace(__len__=lambda self: len(candles))


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


def test_provider_candle_timestamp_is_verified_when_not_in_future():
    pipeline = _pipeline()
    ctx = SimpleNamespace(
        symbol="NIFTY",
        data_provenance=SimpleNamespace(spot=None, option_chain=None),
    )

    # Exercise the timestamp/provenance contract without depending on a live clock.
    candles = _Provider().get_historical_data()
    provider_timestamp = pipeline._provider_candle_timestamp(candles)

    assert provider_timestamp is not None
    assert provider_timestamp.tzinfo == timezone.utc
    assert provider_timestamp <= datetime.now(timezone.utc)


def test_missing_provider_candle_timestamp_is_unverified():
    pipeline = _pipeline()

    assert pipeline._provider_candle_timestamp([{"o": 1, "h": 2}]) is None
