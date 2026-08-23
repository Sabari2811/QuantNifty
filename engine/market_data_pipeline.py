from datetime import datetime, timedelta, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
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
        snapshot = self.provider.next_cycle()
        ctx.timestamp = snapshot.timestamp
        ctx.cycle_no = snapshot.cycle_no
        ctx.symbol = snapshot.symbol
        ctx.spot = snapshot.spot
        ctx.option_chain = snapshot.option_chain.copy()
        ctx.greeks_df = snapshot.greeks.copy()
        ctx.analytics = snapshot.analytics
        ctx.decision = snapshot.decision
        ctx.explanation = snapshot.explanation
        ctx.data_provenance = RuntimeDataProvenance(
            option_chain=ctx.option_chain.attrs.get("data_provenance"),
            candles=None,
            spot=AcquisitionProvenance(
                source="simulation snapshot spot",
                acquired_at=datetime.now(timezone.utc),
                expected_count=1,
                received_count=1,
                missing_count=0,
                freshness_verified=False,
                reasons=("simulation_snapshot",),
            ),
        )
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
        ctx.data_provenance = RuntimeDataProvenance(
            spot=ctx.data_provenance.spot,
            option_chain=ctx.option_chain.attrs.get("data_provenance"),
        )

    def _fetch_historical_candles(self, ctx):
        security_id = self.instrument.get_index_security_id(ctx.symbol)
        if security_id is None:
            raise ValueError(
                f"Index security ID not found for symbol: {ctx.symbol}"
            )

        scrip_code = self.instrument.get_scrip_code("NIDX", security_id)
        end = datetime.now()
        start = end - timedelta(days=5)

        candles = self.provider.get_historical_data(
            scrip_code=scrip_code,
            interval="5minute",
            start_time=int(start.timestamp() * 1000),
            end_time=int(end.timestamp() * 1000),
        )

        ctx.candles = self.candle_manager.to_dataframe(candles)
        ctx.data_provenance = RuntimeDataProvenance(
            spot=ctx.data_provenance.spot,
            option_chain=ctx.data_provenance.option_chain,
            candles=AcquisitionProvenance(
                source=f"INDMoney historical candles:{scrip_code}",
                acquired_at=end.replace(tzinfo=timezone.utc),
                expected_count=1,
                received_count=1 if len(ctx.candles) > 0 else 0,
                missing_count=0 if len(ctx.candles) > 0 else 1,
                freshness_verified=False,
                reasons=(
                    "provider_candle_timestamp_not_used_for_freshness",
                ),
            ),
        )

    def run(self, ctx):
        if isinstance(self.provider, SimulationProvider):
            self._run_replay(ctx)
        else:
            self._run_live(ctx)
