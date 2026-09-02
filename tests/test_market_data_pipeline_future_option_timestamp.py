from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from engine.market_data_pipeline import MarketDataPipeline
from providers.indmoney_websocket import LiveQuoteTick
from providers.live_quote_coordinator import LiveQuoteBatch


def _chain():
    return pd.DataFrame([{
        "Strike": 25000,
        "CE_ID": 111,
        "CE_LTP": 150,
        "CE_OI": 45000,
        "CE_VOLUME": 1200,
        "PE_ID": 222,
        "PE_LTP": 140,
        "PE_OI": 43000,
        "PE_VOLUME": 900,
    }])


def test_future_live_option_timestamp_does_not_create_negative_freshness(monkeypatch):
    pipeline = MarketDataPipeline.__new__(MarketDataPipeline)
    pipeline.provider = object()
    pipeline.instrument = SimpleNamespace(
        get_nearest_weekly_expiry=lambda symbol: "09/08/2026 14:00"
    )
    pipeline.chain_manager = SimpleNamespace(
        get_live_option_chain=lambda symbol, spot, strike_levels: _chain()
    )
    pipeline.live_feed = SimpleNamespace(
        option_instrument=lambda value: f"NFO:{int(value)}",
        collect=lambda instruments, mode: LiveQuoteBatch(
            {"NFO:111": LiveQuoteTick(
                "111",
                datetime(2026, 9, 2, 5, 30, tzinfo=timezone.utc),
                1788327000000,
                "quote",
                {"ltp": 151},
            )},
            datetime(2026, 9, 2, 5, 29, tzinfo=timezone.utc),
            datetime(2026, 9, 2, 5, 29, tzinfo=timezone.utc),
            datetime(2026, 9, 2, 5, 29, tzinfo=timezone.utc),
        ),
    )

    # _fetch_option_chain uses its local wall clock for the provenance age.
    # Pin it so the provider timestamp is unambiguously in the future.
    import engine.market_data_pipeline as module
    fixed_now = datetime(2026, 9, 2, 5, 29, tzinfo=timezone.utc)
    class _Clock:
        @staticmethod
        def now(tz=None):
            return fixed_now
    monkeypatch.setattr(module, "datetime", _Clock)

    existing = AcquisitionProvenance(
        source="INDMoney option quotes",
        expected_count=2,
        received_count=2,
        missing_count=0,
        freshness_verified=False,
        freshness_seconds=None,
    )
    chain = _chain()
    chain.attrs["data_provenance"] = existing
    pipeline.chain_manager.get_live_option_chain = lambda symbol, spot, strike_levels: chain

    ctx = SimpleNamespace(
        symbol="NIFTY",
        spot=25050.0,
        strike_levels=1,
        data_provenance=RuntimeDataProvenance(
            spot=SimpleNamespace(source="spot")
        ),
    )
    pipeline._fetch_option_chain(ctx)

    result = ctx.data_provenance.option_chain
    assert result.freshness_verified is False
    assert result.freshness_seconds is None
    assert result.reasons == ("provider_quote_timestamp_in_future",)
    assert result.provider_timestamp == datetime(2026, 9, 2, 5, 30, tzinfo=timezone.utc)
