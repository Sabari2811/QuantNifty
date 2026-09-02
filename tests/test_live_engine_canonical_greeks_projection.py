from types import SimpleNamespace

import pandas as pd

import engine.live_engine as live_engine_module
from engine.live_engine import LiveEngine


def test_run_analytics_promotes_pipeline_enriched_greeks_to_runtime_context(monkeypatch):
    raw = pd.DataFrame(
        {
            "Strike": [24000],
            "CE_GAMMA": [0.001],
            "PE_GAMMA": [0.0008],
            "CE_OI": [1000],
            "PE_OI": [900],
        }
    )
    enriched = raw.assign(
        CE_GEX=[65.0],
        PE_GEX=[46.8],
        NET_GEX=[18.2],
        NET_DEX=[12.5],
    )

    class FakePipeline:
        def run(self, **kwargs):
            assert kwargs["greeks_df"] is raw
            return {"context": SimpleNamespace(greeks=enriched)}

    captured = {}

    class FakeSnapshot:
        def save(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace()

    engine = LiveEngine.__new__(LiveEngine)
    engine.provider = object()
    engine.ctx = SimpleNamespace(
        greeks_df=raw,
        spot=24100.0,
        candles=None,
    )
    engine._previous_greeks_df = None
    engine.pipeline = FakePipeline()
    engine.greeks = SimpleNamespace(greeks=object())
    engine.market_regime = SimpleNamespace(analyze=lambda snapshot: {})
    engine.decision_engine = SimpleNamespace(build=lambda snapshot: SimpleNamespace())
    engine.explanation_engine = SimpleNamespace(build=lambda **kwargs: {})
    engine.intelligence_service = None
    engine.trade_pipeline = SimpleNamespace(execute=lambda ctx: None)

    monkeypatch.setattr(live_engine_module, "MarketSnapshot", lambda: FakeSnapshot())

    engine._run_analytics()

    assert list(engine.ctx.greeks_df.columns) == list(enriched.columns)
    assert engine.ctx.greeks_df["NET_GEX"].tolist() == [18.2]
    assert engine.ctx.greeks_df["CE_GEX"].tolist() == [65.0]
    assert engine.ctx.greeks_df["PE_GEX"].tolist() == [46.8]
    assert captured["greeks_df"].equals(enriched)
