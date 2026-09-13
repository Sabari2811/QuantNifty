"""Latency-focused NIFTY live engine.

Keeps the existing safety/decision/execution contract but removes the
unnecessary historical-candle REST request from every live cycle. Candles are
refreshed periodically while their real provider timestamp remains the source
of freshness truth. Order execution still occurs before persistence/learning.
"""
from __future__ import annotations

from datetime import datetime, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from engine.live_engine import LiveEngine


class NiftyHotPathEngine(LiveEngine):
    """LiveEngine variant optimized for the NIFTY decision hot path."""

    CANDLE_REFRESH_SECONDS = 60.0

    def __init__(self, *args, **kwargs):
        self._cached_candles = None
        self._cached_candle_provenance = None
        self._cached_candle_at = None
        super().__init__(*args, **kwargs)

    def _refresh_candles_if_needed(self, ctx, force: bool = False):
        now = datetime.now(timezone.utc)
        if (
            not force
            and self._cached_candles is not None
            and self._cached_candle_at is not None
            and (now - self._cached_candle_at).total_seconds() < self.CANDLE_REFRESH_SECONDS
        ):
            ctx.candles = self._cached_candles
            provenance = self._cached_candle_provenance
            if provenance is not None:
                provider_timestamp = provenance.provider_timestamp
                if provider_timestamp is not None:
                    age = (now - provider_timestamp).total_seconds()
                    status = "FRESH" if age <= self.market_pipeline.CANDLE_FRESH_SECONDS else (
                        "AGING" if age <= self.market_pipeline.CANDLE_AGING_SECONDS else "STALE"
                    )
                    fresh = age <= self.market_pipeline.CANDLE_FRESH_SECONDS
                    reasons = ("provider_candle_timestamp",) if fresh else (
                        "provider_candle_timestamp", "provider_candle_aging" if status == "AGING" else "provider_candle_stale"
                    )
                    provenance = AcquisitionProvenance(
                        source=provenance.source,
                        acquired_at=provenance.acquired_at,
                        provider_timestamp=provider_timestamp,
                        expected_count=provenance.expected_count,
                        received_count=provenance.received_count,
                        missing_count=provenance.missing_count,
                        freshness_verified=fresh,
                        freshness_seconds=age,
                        reasons=reasons,
                        freshness_status_override=status,
                    )
                ctx.data_provenance = RuntimeDataProvenance(
                    spot=ctx.data_provenance.spot,
                    option_chain=ctx.data_provenance.option_chain,
                    candles=provenance,
                )
            return

        self.market_pipeline._fetch_historical_candles(ctx)
        self._cached_candles = ctx.candles
        self._cached_candle_provenance = getattr(ctx.data_provenance, "candles", None)
        self._cached_candle_at = now

    def _run_hot_market_data(self, ctx):
        """Fetch only decision-critical live data; candles are cached."""
        self.market_pipeline._fetch_spot(ctx)
        self.market_pipeline._fetch_option_chain(ctx)
        self._refresh_candles_if_needed(ctx)

    def run_cycle(self):
        self.ctx.runtime_status = "RUNNING"
        self.ctx.cycle_no += 1
        self.ctx.timestamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
        try:
            self._run_hot_market_data(self.ctx)
            chain_ready, block_reason = self._option_chain_ready_for_analytics(self.ctx)
            if not chain_ready:
                self.ctx.runtime_status = "DEGRADED"
                self.ctx.trade_status = "BLOCKED"
                self.ctx.trade_block_reason = block_reason
                self.trade_pipeline.sync_context(self.ctx)
                self._sync_risk_snapshot()
                self.recording_manager.record(self.ctx)
                return self.ctx

            closed_before = len(self.paper_broker.portfolio.closed_positions)
            self.paper_broker.update_positions(self.ctx.option_chain)
            if len(self.paper_broker.portfolio.closed_positions) > closed_before:
                position = self.paper_broker.last_trade
                if position is not None:
                    self.risk_manager.on_trade_closed(position)
            self._persist_position_runtime_state()
            self.trade_pipeline.sync_context(self.ctx)
            self._calculate_greeks()
            self._run_analytics()
            self._previous_greeks_df = self.ctx.greeks_df.copy(deep=True)
            self.recording_manager.record(self.ctx)
            return self.ctx
        except Exception:
            from core.logger import logger
            logger.exception("NIFTY HOT PATH ERROR")
            self.ctx.runtime_status = "ERROR"
            raise
        finally:
            if self.ctx.runtime_status not in {"ERROR", "DEGRADED"}:
                self.ctx.runtime_status = "IDLE"
