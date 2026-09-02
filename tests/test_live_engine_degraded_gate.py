from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from core.runtime_context import RuntimeContext
from engine.live_engine import LiveEngine


class _MarketPipeline:
    def run(self, ctx):
        ctx.spot = 25000.0
        ctx.option_chain = object()
        ctx.expiry = "25/08/2026 14:00"
        ctx.data_provenance = RuntimeDataProvenance(
            spot=AcquisitionProvenance(
                source="test spot",
                expected_count=1,
                received_count=1,
                missing_count=0,
                freshness_verified=False,
            ),
            option_chain=AcquisitionProvenance(
                source="test option chain",
                expected_count=10,
                received_count=9,
                missing_count=1,
                freshness_verified=False,
                integrity_status="INVALID",
                reasons=("missing_provider_quotes:1",),
                integrity_reasons=("missing_pe_ltp",),
            ),
        )


class _TradePipeline:
    def __init__(self):
        self.risk_manager = object()
        self.sync_calls = 0
        self.execute_calls = 0

    def sync_context(self, ctx):
        self.sync_calls += 1

    def execute(self, ctx):
        self.execute_calls += 1


class _RecordingManager:
    def __init__(self):
        self.calls = 0

    def record(self, ctx):
        self.calls += 1


def _degraded_engine():
    engine = LiveEngine.__new__(LiveEngine)
    engine.ctx = RuntimeContext()
    engine.provider = object()
    engine.market_pipeline = _MarketPipeline()
    engine.trade_pipeline = _TradePipeline()
    engine.recording_manager = _RecordingManager()
    return engine


def test_invalid_or_partial_option_chain_blocks_analytics():
    engine = _degraded_engine()

    ctx = engine.run_cycle()

    assert ctx.runtime_status == "DEGRADED"
    assert ctx.trade_status == "BLOCKED"
    assert ctx.trade_block_reason == "option_chain_coverage:PARTIAL"
    assert ctx.greeks_df is None
    assert ctx.analytics == {}
    assert ctx.decision is None
    assert ctx.intelligence is None
    assert engine.trade_pipeline.sync_calls == 1
    assert engine.trade_pipeline.execute_calls == 0
    assert engine.recording_manager.calls == 1


def test_complete_valid_option_chain_is_allowed():
    ctx = RuntimeContext()
    ctx.data_provenance = RuntimeDataProvenance(
        option_chain=AcquisitionProvenance(
            source="test option chain",
            expected_count=2,
            received_count=2,
            missing_count=0,
            freshness_verified=False,
            integrity_status="VALID",
        )
    )

    assert LiveEngine._option_chain_ready_for_analytics(ctx) == (True, "")


def test_missing_option_chain_provenance_blocks_analytics():
    ctx = RuntimeContext()

    assert LiveEngine._option_chain_ready_for_analytics(ctx) == (
        False,
        "option_chain_provenance_unavailable",
    )
