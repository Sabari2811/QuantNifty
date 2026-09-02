import os
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from core.data_provenance import AcquisitionProvenance, RuntimeDataProvenance
from core.quote_integrity import assess_option_chain
from core.quote_metadata import extract_provider_timestamp
from providers.indmoney_provider import INDMoneyProvider
from providers.live_quote_coordinator import LiveQuoteCoordinator
from providers.simulation_provider import SimulationProvider


class MarketDataPipeline:
    """Prepare RuntimeContext with live or replay market data."""

    CANDLE_FRESH_SECONDS = 5 * 60
    CANDLE_AGING_SECONDS = 15 * 60
    CANDLE_STALE_SECONDS = 30 * 60

    def __init__(self, provider, instrument, market, chain_manager, candle_manager):
        self.provider = provider
        self.instrument = instrument
        self.market = market
        self.chain_manager = chain_manager
        self.candle_manager = candle_manager
        self.live_feed = None
        if os.getenv("INDSTOCKS_ENABLE_WS_LIVE_QUOTES", "0") == "1" and isinstance(provider, INDMoneyProvider):
            token = getattr(provider, "token", None) or os.getenv("INDSTOCKS_API_TOKEN")
            if not token:
                raise RuntimeError("INDSTOCKS_ENABLE_WS_LIVE_QUOTES=1 requires INDSTOCKS_API_TOKEN")
            self.live_feed = LiveQuoteCoordinator(token)

    @classmethod
    def _candle_freshness(cls, provider_timestamp, acquired_at):
        if provider_timestamp is None:
            return False, None, "UNVERIFIED", ("provider_candle_timestamp_unavailable",)
        if provider_timestamp > acquired_at:
            return False, None, "UNVERIFIED", ("provider_candle_timestamp_in_future",)
        age = (acquired_at - provider_timestamp).total_seconds()
        if age <= cls.CANDLE_FRESH_SECONDS:
            return True, age, "FRESH", ("provider_candle_timestamp",)
        if age <= cls.CANDLE_AGING_SECONDS:
            return False, age, "AGING", ("provider_candle_timestamp", "provider_candle_aging")
        return False, age, "STALE", ("provider_candle_timestamp", "provider_candle_stale")

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
        ctx.replay_expected_analytics = snapshot.analytics
        ctx.data_provenance = snapshot.data_provenance
        ctx.candles = None

    @staticmethod
    def _quote_freshness(quote, acquired_at):
        provider_timestamp = extract_provider_timestamp(quote)
        if provider_timestamp is None:
            return None, False, None, ("provider_quote_timestamp_unavailable",)
        if provider_timestamp > acquired_at:
            return provider_timestamp, False, None, ("provider_quote_timestamp_in_future",)
        return provider_timestamp, True, (acquired_at - provider_timestamp).total_seconds(), ("provider_quote_timestamp",)

    @staticmethod
    def _tick_quote(tick):
        data = dict(tick.data)
        data["provider_timestamp"] = tick.timestamp_ms
        if tick.ltp is not None:
            data["ltp"] = tick.ltp
            data["live_price"] = tick.ltp
        return data

    def _fetch_spot(self, ctx):
        acquired_at = datetime.now(timezone.utc)
        quote = self.market.get_spot_quote(ctx.symbol)
        if self.live_feed is not None:
            security_id = self.instrument.get_index_security_id(ctx.symbol)
            if security_id is None:
                raise RuntimeError(f"Unable to resolve WebSocket index security ID for {ctx.symbol}")
            ws_instrument = self.live_feed.index_instrument(security_id)
            batch = self.live_feed.collect([ws_instrument], mode="quote")
            tick = batch.ticks.get(ws_instrument)
            if tick is not None:
                quote = self._tick_quote(tick)
                acquired_at = batch.acquired_at
        if quote is None:
            raise Exception("Unable to fetch live quote.")
        price = None
        for key in ("ltp", "LTP", "last_price", "lastPrice", "live_price", "close"):
            if quote.get(key) is not None:
                price = float(quote[key])
                break
        if price is None:
            raise Exception(f"Spot price not found in response: {quote}")
        ctx.spot = price
        provider_timestamp, freshness_verified, freshness_seconds, reasons = self._quote_freshness(quote, acquired_at)
        ctx.data_provenance = RuntimeDataProvenance(spot=AcquisitionProvenance(source="INDMoney index quote", acquired_at=acquired_at, provider_timestamp=provider_timestamp, expected_count=1, received_count=1, missing_count=0, freshness_verified=freshness_verified, freshness_seconds=freshness_seconds, reasons=reasons))

    def _fetch_option_chain(self, ctx):
        ctx.expiry = self.instrument.get_nearest_weekly_expiry(ctx.symbol)
        ctx.option_chain = self.chain_manager.get_live_option_chain(ctx.symbol, ctx.spot, ctx.strike_levels)
        acquired_at = datetime.now(timezone.utc)
        if self.live_feed is not None and not ctx.option_chain.empty:
            instruments = []
            instrument_map = {}
            for column in ("CE_ID", "PE_ID"):
                if column in ctx.option_chain.columns:
                    for value in ctx.option_chain[column].dropna():
                        websocket_id = self.live_feed.option_instrument(value)
                        instruments.append(websocket_id)
                        instrument_map[websocket_id] = int(value)
            option_timestamp = None
            if instruments:
                batch = self.live_feed.collect(instruments, mode="quote")
                acquired_at = batch.acquired_at
                option_timestamp = batch.latest_provider_timestamp
                for id_column, price_column in (("CE_ID", "CE_LTP"), ("PE_ID", "PE_LTP")):
                    if id_column not in ctx.option_chain.columns or price_column not in ctx.option_chain.columns:
                        continue
                    for index, security_id in ctx.option_chain[id_column].items():
                        ws_instrument = self.live_feed.option_instrument(security_id)
                        tick = batch.ticks.get(ws_instrument)
                        if tick is not None and tick.ltp is not None:
                            ctx.option_chain.at[index, price_column] = tick.ltp
        else:
            option_timestamp = None
        option_provenance = ctx.option_chain.attrs.get("data_provenance")
        if option_provenance is None:
            option_provenance = AcquisitionProvenance(source="INDMoney option quotes", expected_count=len(ctx.option_chain) * 2, received_count=len(ctx.option_chain) * 2, missing_count=0, freshness_verified=False, reasons=("provider_quote_timestamp_unavailable",))
        if option_timestamp is not None:
            freshness_verified = option_timestamp <= acquired_at
            freshness_seconds = (acquired_at - option_timestamp).total_seconds() if freshness_verified else None
            freshness_reasons = ("provider_quote_timestamp",) if freshness_verified else ("provider_quote_timestamp_in_future",)
            option_provenance = replace(option_provenance, provider_timestamp=option_timestamp, freshness_verified=freshness_verified, freshness_seconds=freshness_seconds, reasons=freshness_reasons)
        integrity = assess_option_chain(ctx.option_chain, ctx.spot)
        option_provenance = replace(option_provenance, integrity_status=integrity.status, integrity_reasons=integrity.reasons)
        ctx.option_chain.attrs["quote_integrity"] = integrity.as_dict()
        ctx.option_chain.attrs["data_provenance"] = option_provenance
        ctx.data_provenance = RuntimeDataProvenance(spot=ctx.data_provenance.spot, option_chain=option_provenance)

    @staticmethod
    def _provider_candle_timestamp(candles):
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
        candles = self.provider.get_historical_data(scrip_code=scrip_code, interval="5minute", start_time=int(start.timestamp() * 1000), end_time=int(end.timestamp() * 1000))
        ctx.candles = self.candle_manager.to_dataframe(candles)
        provider_timestamp = self._provider_candle_timestamp(candles)
        freshness_verified, freshness_seconds, freshness_status, freshness_reasons = self._candle_freshness(provider_timestamp, end)
        ctx.data_provenance = RuntimeDataProvenance(spot=ctx.data_provenance.spot, option_chain=ctx.data_provenance.option_chain, candles=AcquisitionProvenance(source=f"INDMoney historical candles:{scrip_code}", acquired_at=end, provider_timestamp=provider_timestamp, expected_count=1, received_count=1 if len(ctx.candles) > 0 else 0, missing_count=0 if len(ctx.candles) > 0 else 1, freshness_verified=freshness_verified, freshness_seconds=freshness_seconds, reasons=freshness_reasons, freshness_status_override=freshness_status))

    def run(self, ctx):
        if isinstance(self.provider, SimulationProvider):
            self._run_replay(ctx)
        else:
            self._run_live(ctx)
