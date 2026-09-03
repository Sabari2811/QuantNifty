from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor
from models.market_context import MarketContext


class MarketExtractor(BaseExtractor):
    """
    Extracts market-level intelligence from RuntimeContext.

    This extractor performs field mapping only.
    It does not calculate or reinterpret analytics.

    The typed RuntimeContext.market_context is the canonical analytics
    source. The legacy RuntimeContext.analytics dictionary remains a
    compatibility fallback for older callers/snapshots that do not populate
    the typed fields.
    """

    @staticmethod
    def _mapping(value):
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _number(value, default=0.0):
        if value is None:
            return default

        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _canonical_mapping(market_context, analytics, field_name):
        """Return typed canonical mapping, falling back only when empty.

        A default/empty MarketContext is common in legacy unit callers. In
        that case the established serialized projection remains usable. When
        the typed field contains data, it always wins over the compatibility
        projection, preventing silent divergence from changing intelligence.
        """
        typed = MarketExtractor._mapping(
            getattr(market_context, field_name, None)
        )
        if typed:
            return typed
        return MarketExtractor._mapping(
            analytics.get(field_name, {})
        )

    def extract(
        self,
        ctx,
        record,
    ) -> None:

        analytics = self._mapping(
            getattr(ctx, "analytics", None)
        )

        market_context = getattr(
            ctx,
            "market_context",
            None,
        )

        if not isinstance(market_context, MarketContext):
            market_context = None

        snapshot = getattr(
            ctx,
            "snapshot",
            None,
        )

        timestamp = getattr(
            snapshot,
            "timestamp",
            None,
        )

        if timestamp is None:
            timestamp = getattr(
                ctx,
                "timestamp",
                None,
            )

        from datetime import datetime

        if isinstance(timestamp, datetime):
            record.timestamp = timestamp

        record.trading_day = getattr(
            ctx,
            "trading_day",
            getattr(
                snapshot,
                "trading_day",
                "",
            ),
        ) or ""

        record.expiry = getattr(
            ctx,
            "expiry",
            "",
        ) or ""

        record.session = getattr(
            ctx,
            "session",
            getattr(
                snapshot,
                "session",
                "",
            ),
        ) or ""

        record.spot_price = self._number(
            getattr(
                ctx,
                "spot",
                getattr(market_context, "spot", 0.0),
            )
        )

        expected_move = self._canonical_mapping(
            market_context,
            analytics,
            "expected_move",
        )

        record.atm_strike = self._number(
            expected_move.get("atm_strike", 0.0)
        )

        record.futures_price = self._number(
            getattr(
                ctx,
                "futures_price",
                analytics.get("futures_price", 0.0),
            )
        )

        record.india_vix = self._number(
            getattr(
                ctx,
                "india_vix",
                analytics.get("india_vix", 0.0),
            )
        )

        market_structure = self._canonical_mapping(
            market_context,
            analytics,
            "market_structure",
        )

        technical = self._canonical_mapping(
            market_context,
            analytics,
            "technical",
        )

        ema = self._mapping(
            technical.get(
                "ema",
                technical.get("EMA", {}),
            )
        )

        record.trend = str(
            ema.get("trend", "") or ""
        )

        record.market_structure = str(
            market_structure.get("structure", "") or ""
        )

        institutional_score = self._canonical_mapping(
            market_context,
            analytics,
            "institutional_score",
        )

        institutional = self._mapping(
            institutional_score.get("institutional", {})
        )

        record.institutional_bias = str(
            institutional.get("bias", "") or ""
        )

        probability = self._canonical_mapping(
            market_context,
            analytics,
            "probability",
        )

        record.probability = self._number(
            probability.get("bullish_probability", 0.0)
        )

        ad = self._mapping(
            technical.get("ad_ratio", {})
        )

        if ad:
            record.ad_ratio = self._number(
                ad.get("value", ad.get("ratio", 0.0))
            )

        pcr = self._canonical_mapping(
            market_context,
            analytics,
            "pcr",
        )

        record.pcr = self._number(
            pcr.get("oi_pcr", pcr.get("pcr", 0.0))
        )

        rsi = self._mapping(
            technical.get("rsi", {})
        )

        record.rsi = self._number(
            rsi.get("rsi", 0.0)
        )

        atr = self._canonical_mapping(
            market_context,
            analytics,
            "atr",
        )

        record.atr = self._number(
            atr.get("atr", 0.0)
        )

        adx = self._mapping(
            technical.get("adx", {})
        )

        record.adx = self._number(
            adx.get("adx", 0.0)
        )

        vwap = self._mapping(
            technical.get("vwap", {})
        )

        record.vwap_distance = self._number(
            vwap.get("distance", 0.0)
        )

        record.expected_move = self._number(
            expected_move.get("expected_move", 0.0)
        )

        record.expected_probability = self._number(
            expected_move.get(
                "probability",
                expected_move.get("expected_probability", 0.0),
            )
        )
