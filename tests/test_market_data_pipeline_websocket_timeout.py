from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from engine.market_data_pipeline import MarketDataPipeline
from providers.indmoney_websocket import LiveQuoteReceiveTimeout


def _chain():
    chain = pd.DataFrame([
        {
            "Strike": 25000,
            "CE_ID": 111,
            "CE_LTP": 150.0,
            "CE_OI": 45000,
            "CE_VOLUME": 1200,
            "PE_ID": 222,
            "PE_LTP": 140.0,
            "PE_OI": 43000,
            "PE_VOLUME": 900,
        }
    ])
    chain.attrs["data_provenance"] = AcquisitionProvenance(
        source="INDMoney option quotes",
        expected_count=2,
        received_count=2,
        missing_count=0,
        freshness_verified=False,
        freshness_seconds=None,
        reasons=("provider_quote_timestamp_unavailable",),
    )
    return chain


def _pipeline(chain):
    pipeline = MarketDataPipeline.__new__(MarketDataPipeline)
    pipeline.provider = object()
    pipeline.instrument = SimpleNamespace(
        get_nearest_weekly_expiry=lambda symbol: "09/08/2026 14:00"
    )
    pipeline.chain_manager = SimpleNamespace(
        get_live_option_chain=lambda symbol, spot, strike_levels: chain
    )
    pipeline.live_feed = SimpleNamespace(
        option_instrument=lambda value: f"NFO:{int(value)}",
        collect=lambda instruments, mode: (_ for _ in ()).throw(
            LiveQuoteReceiveTimeout("WebSocket price receive exceeded 10.0s")
        ),
    )
    return pipeline


def test_option_websocket_timeout_preserves_complete_rest_chain():
    chain = _chain()
    pipeline = _pipeline(chain)
    ctx = SimpleNamespace(
        symbol="NIFTY",
        spot=25050.0,
        strike_levels=1,
        data_provenance=RuntimeDataProvenance(
            spot=SimpleNamespace(source="spot")
        ),
    )

    pipeline._fetch_option_chain(ctx)

    assert ctx.option_chain is chain
    assert ctx.option_chain.loc[0, "CE_LTP"] == 150.0
    assert ctx.option_chain.loc[0, "PE_LTP"] == 140.0
    provenance = ctx.data_provenance.option_chain
    assert provenance.coverage_status == "COMPLETE"
    assert provenance.freshness_verified is False
    assert provenance.freshness_seconds is None
    assert "websocket_quote_receive_timeout" in provenance.reasons
    assert provenance.provider_timestamp is None
    assert ctx.option_chain.attrs["quote_integrity"]["status"] in {"VALID", "SUSPECT"}


def test_spot_websocket_timeout_falls_back_to_rest_quote(monkeypatch):
    pipeline = MarketDataPipeline.__new__(MarketDataPipeline)
    pipeline.market = SimpleNamespace(
        get_spot_quote=lambda symbol: {
            "ltp": 25050.0,
            "provider_timestamp": datetime(2026, 9, 2, 5, 30, tzinfo=timezone.utc),
        }
    )
    pipeline.instrument = SimpleNamespace(
        get_index_security_id=lambda symbol: 26000
    )
    pipeline.live_feed = SimpleNamespace(
        index_instrument=lambda security_id: "NIDX:26000",
        collect=lambda instruments, mode: (_ for _ in ()).throw(
            LiveQuoteReceiveTimeout("WebSocket price receive exceeded 10.0s")
        ),
    )
    ctx = SimpleNamespace(symbol="NIFTY")

    pipeline._fetch_spot(ctx)

    assert ctx.spot == 25050.0
    assert ctx.data_provenance.spot.freshness_verified is True
    assert ctx.data_provenance.spot.provider_timestamp == datetime(
        2026, 9, 2, 5, 30, tzinfo=timezone.utc
    )
