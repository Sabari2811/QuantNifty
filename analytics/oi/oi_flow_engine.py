from __future__ import annotations

import pandas as pd


class OIFlowEngine:
    """
    Institutional Open Interest Flow Engine.

    Flow classification is based on ΔPrice and ΔOI:

        ↑ Price + ↑ OI  -> LONG_BUILDUP
        ↓ Price + ↑ OI  -> SHORT_BUILDUP
        ↑ Price + ↓ OI  -> SHORT_COVERING
        ↓ Price + ↓ OI  -> LONG_UNWINDING

    Runtime behavior
    ----------------
    First snapshot:
        No previous snapshot exists.
        Flow is marked UNKNOWN.
        Status = AWAITING_PREVIOUS_SNAPSHOT.

    Subsequent snapshots:
        ΔPrice and ΔOI are calculated against the previous
        successful market snapshot.
        Status = READY.

    Backward compatibility
    ----------------------
    When _classify() is called directly, it preserves the
    existing classification contract used by the unit tests.
    """

    FLOW_TYPES = [
        "LONG_BUILDUP",
        "SHORT_BUILDUP",
        "LONG_UNWINDING",
        "SHORT_COVERING",
        "UNKNOWN",
    ]

    def __init__(self):
        pass

    # ==========================================================
    # FLOW CLASSIFICATION
    # ==========================================================

    def _classify(self, price: float, oi: float) -> str:
        """
        Classify flow from signed price/OI changes.

        Parameters
        ----------
        price:
            Price change.

        oi:
            Open-interest change.
        """

        if price == 0 and oi == 0:
            return "UNKNOWN"

        if price > 0 and oi > 0:
            return "LONG_BUILDUP"

        if price <= 0 and oi > 0:
            return "SHORT_BUILDUP"

        if price > 0 and oi <= 0:
            return "SHORT_COVERING"

        return "LONG_UNWINDING"

    # ==========================================================
    # FLOW COUNTS
    # ==========================================================

    def _count_flow(self, series: pd.Series) -> dict:
        """
        Count every supported flow type.
        """

        return {
            flow.lower(): int((series == flow).sum())
            for flow in self.FLOW_TYPES
        }

    # ==========================================================
    # MARKET BIAS
    # ==========================================================

    def _market_bias(
        self,
        ce_summary: dict,
        pe_summary: dict,
    ) -> str:
        """
        Calls:

            PUT long buildup > CALL long buildup
                -> BULLISH

            CALL long buildup > PUT long buildup
                -> BEARISH

            Otherwise
                -> NEUTRAL
        """

        call_long = ce_summary["long_buildup"]
        put_long = pe_summary["long_buildup"]

        if put_long > call_long:
            return "BULLISH"

        if call_long > put_long:
            return "BEARISH"

        return "NEUTRAL"

    # ==========================================================
    # TREND
    # ==========================================================

    def _trend(
        self,
        ce_summary: dict,
        pe_summary: dict,
    ) -> str:
        """
        Determine whether OI flow is trending, reversing,
        or sideways.
        """

        total_long = (
            ce_summary["long_buildup"]
            + pe_summary["long_buildup"]
        )

        total_cover = (
            ce_summary["short_covering"]
            + pe_summary["short_covering"]
        )

        if total_long > total_cover:
            return "TRENDING"

        if total_cover > total_long:
            return "REVERSAL"

        return "SIDEWAYS"

    # ==========================================================
    # NUMERIC NORMALIZATION
    # ==========================================================

    @staticmethod
    def _numeric(
        df: pd.DataFrame,
        column: str,
    ) -> pd.Series:
        """
        Safely convert a dataframe column to numeric.
        """

        if column not in df.columns:
            return pd.Series(
                0.0,
                index=df.index,
            )

        return (
            pd.to_numeric(
                df[column],
                errors="coerce",
            )
            .fillna(0.0)
        )

    # ==========================================================
    # PREVIOUS SNAPSHOT ALIGNMENT
    # ==========================================================

    def _prepare_previous(
        self,
        previous_greeks_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Normalize the previous snapshot so that it can be
        joined against the current snapshot using Strike.
        """

        previous = previous_greeks_df.copy()

        if "Strike" not in previous.columns:

            if "STRIKE" in previous.columns:
                previous = previous.rename(
                    columns={
                        "STRIKE": "Strike"
                    }
                )

        if "Strike" not in previous.columns:
            return pd.DataFrame()

        previous["Strike"] = pd.to_numeric(
            previous["Strike"],
            errors="coerce",
        )

        previous = previous.dropna(
            subset=["Strike"]
        )

        required = [
            "CE_LTP",
            "CE_OI",
            "PE_LTP",
            "PE_OI",
        ]

        for column in required:

            if column not in previous.columns:
                previous[column] = 0.0

            previous[column] = self._numeric(
                previous,
                column,
            )

        previous = previous[
            [
                "Strike",
                "CE_LTP",
                "CE_OI",
                "PE_LTP",
                "PE_OI",
            ]
        ].copy()

        return previous

    # ==========================================================
    # FIRST SNAPSHOT
    # ==========================================================

    def _first_snapshot(
        self,
        df: pd.DataFrame,
    ) -> dict:
        """
        First cycle cannot determine ΔPrice/ΔOI.

        We deliberately mark all flow classifications UNKNOWN.
        """

        df["CE_FLOW"] = "UNKNOWN"
        df["PE_FLOW"] = "UNKNOWN"

        df["CE_PRICE_CHANGE"] = 0.0
        df["PE_PRICE_CHANGE"] = 0.0

        df["CE_OI_CHANGE"] = 0.0
        df["PE_OI_CHANGE"] = 0.0

        ce_summary = self._count_flow(
            df["CE_FLOW"]
        )

        pe_summary = self._count_flow(
            df["PE_FLOW"]
        )

        summary = {
            "status": "AWAITING_PREVIOUS_SNAPSHOT",

            "call": ce_summary,

            "put": pe_summary,

            "market_bias": "NEUTRAL",

            "trend": "SIDEWAYS",

            "total_strikes": len(df),
        }

        return {
            "summary": summary,
            "table": df,
        }

    # ==========================================================
    # DELTA ANALYSIS
    # ==========================================================

    def _calculate_deltas(
        self,
        current: pd.DataFrame,
        previous: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate ΔPrice and ΔOI by Strike.
        """

        if previous.empty:

            return current

        previous = previous.rename(
            columns={
                "CE_LTP": "PREV_CE_LTP",
                "CE_OI": "PREV_CE_OI",
                "PE_LTP": "PREV_PE_LTP",
                "PE_OI": "PREV_PE_OI",
            }
        )

        merged = current.merge(
            previous,
            on="Strike",
            how="left",
        )

        for column in [
            "PREV_CE_LTP",
            "PREV_CE_OI",
            "PREV_PE_LTP",
            "PREV_PE_OI",
        ]:

            merged[column] = (
                pd.to_numeric(
                    merged[column],
                    errors="coerce",
                )
                .fillna(0.0)
            )

        merged["CE_PRICE_CHANGE"] = (
            merged["CE_LTP"]
            - merged["PREV_CE_LTP"]
        )

        merged["PE_PRICE_CHANGE"] = (
            merged["PE_LTP"]
            - merged["PREV_PE_LTP"]
        )

        merged["CE_OI_CHANGE"] = (
            merged["CE_OI"]
            - merged["PREV_CE_OI"]
        )

        merged["PE_OI_CHANGE"] = (
            merged["PE_OI"]
            - merged["PREV_PE_OI"]
        )

        return merged

    # ==========================================================
    # MAIN ANALYSIS
    # ==========================================================

    def analyze(
        self,
        greeks_df: pd.DataFrame,
        previous_greeks_df: pd.DataFrame | None = None,
    ):
        """
        Analyze current option-chain OI flow.

        Parameters
        ----------
        greeks_df:
            Current Greeks/options dataframe.

        previous_greeks_df:
            Previous successful cycle's Greeks dataframe.

        Returns
        -------
        dict
            {
                "summary": {...},
                "table": dataframe
            }
        """

        # ------------------------------------------------------
        # Empty input
        # ------------------------------------------------------

        if greeks_df is None or greeks_df.empty:

            return {
                "summary": {},
                "table": greeks_df,
            }

        df = greeks_df.copy()

        # ------------------------------------------------------
        # Normalize Strike
        # ------------------------------------------------------

        if "Strike" not in df.columns:

            if "STRIKE" in df.columns:

                df = df.rename(
                    columns={
                        "STRIKE": "Strike"
                    }
                )

        if "Strike" not in df.columns:

            df["Strike"] = range(
                len(df)
            )

        df["Strike"] = pd.to_numeric(
            df["Strike"],
            errors="coerce",
        )

        # ------------------------------------------------------
        # Normalize current values
        # ------------------------------------------------------

        required = [
            "CE_LTP",
            "CE_OI",
            "PE_LTP",
            "PE_OI",
        ]

        for column in required:

            df[column] = self._numeric(
                df,
                column,
            )

        # ------------------------------------------------------
        # First snapshot
        # ------------------------------------------------------

        if (
            previous_greeks_df is None
            or previous_greeks_df.empty
        ):

            return self._first_snapshot(
                df
            )

        # ------------------------------------------------------
        # Prepare previous snapshot
        # ------------------------------------------------------

        previous = self._prepare_previous(
            previous_greeks_df
        )

        if previous.empty:

            return self._first_snapshot(
                df
            )

        # ------------------------------------------------------
        # Calculate ΔPrice / ΔOI
        # ------------------------------------------------------

        df = self._calculate_deltas(
            df,
            previous,
        )

        # ------------------------------------------------------
        # CE Flow
        # ------------------------------------------------------

        df["CE_FLOW"] = df.apply(
            lambda row: self._classify(
                float(
                    row["CE_PRICE_CHANGE"]
                ),
                float(
                    row["CE_OI_CHANGE"]
                ),
            ),
            axis=1,
        )

        # ------------------------------------------------------
        # PE Flow
        # ------------------------------------------------------

        df["PE_FLOW"] = df.apply(
            lambda row: self._classify(
                float(
                    row["PE_PRICE_CHANGE"]
                ),
                float(
                    row["PE_OI_CHANGE"]
                ),
            ),
            axis=1,
        )

        # ------------------------------------------------------
        # Summary
        # ------------------------------------------------------

        ce_summary = self._count_flow(
            df["CE_FLOW"]
        )

        pe_summary = self._count_flow(
            df["PE_FLOW"]
        )

        summary = {
            "status": "READY",

            "call": ce_summary,

            "put": pe_summary,

            "market_bias": self._market_bias(
                ce_summary,
                pe_summary,
            ),

            "trend": self._trend(
                ce_summary,
                pe_summary,
            ),

            "total_strikes": len(df),
        }

        return {
            "summary": summary,
            "table": df,
        }