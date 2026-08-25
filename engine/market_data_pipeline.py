from dataclasses import replace
from datetime import datetime, timedelta, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from core.quote_integrity import assess_option_chain
from providers.simulation_provider import SimulationProvider


class MarketDataPipeline:
    """Prepare RuntimeContext with live or replay market data."""

    def __init__(self, provider, instrument, market, chain_manager, candle_manager):
        self.provider = provider
        self.instrument = instrument
        self.market = market
        self.chain_manager = chain_manager
        self.candle_manager = candle_manager

    def _run_live(self, ctx):
        self._fetch_spot(ctx)
        self._fetch_option_chain(ctx)
        self._fetch_historical_candles(ctx)

    def _run_replay(self, ctx):
        snapshot = self.provider.current_snapshot()
        ctx.timestamp = snapshot.timestamp
        ctx.cycle_no = snapshot.cycle_no
        ctx.symbol = snapshot.symbol
        ctx.spot = snapshot.spot
        ctx.option_chain = snapshot.option_chain.copy()
        ctx.greeks_df = snapshot.greeks.copy()
        ctx.analytics = snapshot.analytics
        ctx.decision = snapshot.decision
        ctx.explanation = snapshot.explanation
        ctx.intelligence = snapshot.intelligence
        ctx.replay_expected_decision = snapshot.decision
        ctx.replay_expected_intelligence = snapshot.intelligence
        ctx.data_provenance = snapshot.data_provenance
        ctx.candles = None

    def _fetch_spot(self, ctx):
        acquired_at = datetime.now(timezone.utc)
        ctx.spot = self.market.get_spot_price(ctx.symbol)
        ctx.data_provenance = RuntimeDataProvenance(
            spot=AcquisitionProvenance(
                source="INDMoney index quote",
                acquired_at=acquired_at,
                expected_count=1,
                received_count=1 if ctx.spot is not None else 0,
                missing_count=0 if ctx.spot is not None else 1,
                freshness_verified=False,
                reasons=("provider_quote_timestamp_unavailable",),
            )
        )

    def _fetch_option_chain(self, ctx):
        ctx.expiry = self.instrument.get_nearest_weekly_expiry(ctx.symbol)
        ctx.option_chain = self.chain_manager.get_live_option_chain(
            ctx.symbol,
            ctx.spot,
            ctx.strike_levels,
        )

        option_provenance = ctx.option_chain.attrs.get("data_provenance")
        if option_provenance is None:
            option_provenance = AcquisitionProvenance(
                source="INDMoney option quotes",
                expected_count=len(ctx.option_chain),
                received_count=len(ctx.option_chain),
                missing_count=0,
                freshness_verified=False,
                reasons=("provider_quote_timestamp_unavailable",),
            )

        integrity = assess_option_chain(ctx.option_chain, ctx.spot)
        option_provenance = replace(
            option_provenance,
            integrity_status=integrity.status,
            integrity_reasons=integrity.reasons,
        )
        ctx.option_chain.attrs["quote_integrity"] = integrity.as_dict()
        ctx.option_chain.attrs["data_provenance"] = option_provenance

        ctx.data_provenance = RuntimeDataProvenance(
            spot=ctx.data_provenance.spot,
            option_chain=option_provenance,
        )

    @staticmethod
    def _provider_candle_timestamp(candles):
        """Return the newest provider candle timestamp as an aware UTC datetime."""
        timestamps = []
        for candle in candles or []:
            value = candle.get("ts") if isinstance(candle, dict) else None
            if value is None:
                continue
            try:
                timestamp = float(value)
                if timestamp > 1_000_000_000_000:
                    timestamp /= 1000.0
                timestamps.append(datetime.fromtimestamp(timestamp, tz=timezone.utc))
            except (TypeError, ValueError, OverflowError, OSError):
                continue
        return max(timestamps) if timestamps else None

    def _fetch_historical_candles(self, ctx):
        security_id = self.instrument.get_index_security_id(ctx.symbol)
        if security_id is None:
            raise ValueError(f"Index security ID not found for symbol: {ctx.symbol}")

        scrip_code = self.instrument.get_scrip_code("NIDX", security_id)
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=5)

        candles = self.provider.get_historical_data(
            scrip_code=scrip_code,
            interval="5minute",
            start_time=int(start.timestamp() * 1000),
            end_time=int(end.timestamp() * 1000),
        )

        ctx.candles = self.candle_manager.to_dataframe(candles)
        provider_timestamp = self._provider_candle_timestamp(candles)
        if provider_timestamp is None:
            freshness_verified = False
            freshness_seconds = None
            freshness_reasons = ("provider_candle_timestamp_unavailable",)
        elif provider_timestamp > end:
            freshness_verified = False
            freshness_seconds = None
            freshness_reasons = ("provider_candle_timestamp_in_future",)
        else:
            freshness_verified = True
            freshness_seconds = (end - provider_timestamp).total_seconds()
            freshness_reasons = ("provider_candle_timestamp",)

        ctx.data_provenance = RuntimeDataProvenance(
            spot=ctx.data_provenance.spot,
            option_chain=ctx.data_provenance.option_chain,
            candles=AcquisitionProvenance(
                source=f"INDMoney historical candles:{scrip_code}",
                acquired_at=end,
                provider_timestamp=provider_timestamp,
                expected_count=1,
                received_count=1 if len(ctx.candles) > 0 else 0,
                missing_count=0 if len(ctx.candles) > 0 else 1,
                freshness_verified=freshness_verified,
                freshness_seconds=freshness_seconds,
                reasons=freshness_reasons,
            ),
        )

    def run(self, ctx):
        if isinstance(self.provider, SimulationProvider):
            self._run_replay(ctx)
        else:
            self._run_live(ctx)
