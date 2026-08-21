from __future__ import annotations

from datetime import datetime

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class MarketExtractor(BaseExtractor):
    """
    Extracts market-level intelligence from RuntimeContext.

    This extractor performs field mapping only.
    It does not calculate or reinterpret analytics.
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

    def extract(
        self,
        ctx,
        record,
    ) -> None:

        analytics = self._mapping(
            getattr(ctx, "analytics", None)
        )

        snapshot = getattr(
            ctx,
            "snapshot",
            None,
        )

        #
        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------
        #

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

        #
        # ------------------------------------------------------
        # Market
        # ------------------------------------------------------
        #

        record.spot_price = self._number(
            getattr(
                ctx,
                "spot",
                0.0,
            )
        )

        expected_move = self._mapping(
            analytics.get(
                "expected_move",
                {},
            )
        )

        record.atm_strike = self._number(
            expected_move.get(
                "atm_strike",
                0.0,
            )
        )

        # These are intentionally read only if an authoritative
        # runtime/analytics source actually exposes them.
        record.futures_price = self._number(
            getattr(
                ctx,
                "futures_price",
                analytics.get(
                    "futures_price",
                    0.0,
                ),
            )
        )

        record.india_vix = self._number(
            getattr(
                ctx,
                "india_vix",
                analytics.get(
                    "india_vix",
                    0.0,
                ),
            )
        )

        #
        # ------------------------------------------------------
        # Market Structure
        # ------------------------------------------------------
        #

        market_structure = self._mapping(
            analytics.get(
                "market_structure",
                {},
            )
        )

        technical = self._mapping(
            analytics.get(
                "technical",
                {},
            )
        )

        ema = self._mapping(
            technical.get(
                "ema",
                technical.get(
                    "EMA",
                    {},
                ),
            )
        )

        record.trend = str(
            ema.get(
                "trend",
                "",
            )
            or ""
        )

        record.market_structure = str(
            market_structure.get(
                "structure",
                "",
            )
            or ""
        )

        #
        # ------------------------------------------------------
        # Institutional / Probability
        # ------------------------------------------------------
        #

        institutional_score = self._mapping(
            analytics.get(
                "institutional_score",
                {},
            )
        )

        institutional = self._mapping(
            institutional_score.get(
                "institutional",
                {},
            )
        )

        record.institutional_bias = str(
            institutional.get(
                "bias",
                "",
            )
            or ""
        )

        probability = self._mapping(
            analytics.get(
                "probability",
                {},
            )
        )

        record.probability = self._number(
            probability.get(
                "bullish_probability",
                0.0,
            )
        )

        #
        # ------------------------------------------------------
        # Technicals
        # ------------------------------------------------------
        #

        ad = self._mapping(
            technical.get(
                "ad_ratio",
                {}
            )
        )

        if ad:
            record.ad_ratio = self._number(
                ad.get(
                    "value",
                    ad.get(
                        "ratio",
                        0.0,
                    ),
                )
            )

        pcr = self._mapping(
            analytics.get(
                "pcr",
                {},
            )
        )

        record.pcr = self._number(
            pcr.get(
                "oi_pcr",
                pcr.get(
                    "pcr",
                    0.0,
                ),
            )
        )

        rsi = self._mapping(
            technical.get(
                "rsi",
                {},
            )
        )

        record.rsi = self._number(
            rsi.get(
                "rsi",
                0.0,
            )
        )

        atr = self._mapping(
            analytics.get(
                "atr",
                {},
            )
        )

        record.atr = self._number(
            atr.get(
                "atr",
                0.0,
            )
        )

        adx = self._mapping(
            technical.get(
                "adx",
                {},
            )
        )

        record.adx = self._number(
            adx.get(
                "adx",
                0.0,
            )
        )

        vwap = self._mapping(
            technical.get(
                "vwap",
                {},
            )
        )

        record.vwap_distance = self._number(
            vwap.get(
                "distance",
                0.0,
            )
        )

        #
        # ------------------------------------------------------
        # Expected Move / AI fields
        # ------------------------------------------------------
        #

        record.expected_move = self._number(
            expected_move.get(
                "expected_move",
                0.0,
            )
        )

        record.expected_probability = self._number(
            expected_move.get(
                "probability",
                expected_move.get(
                    "expected_probability",
                    0.0,
                ),
            )
        )
