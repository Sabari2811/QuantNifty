import pandas as pd


class OIFlowEngine:
    """
    Institutional Open Interest Flow Engine

    Classification

        ↑ Price + ↑ OI  -> LONG_BUILDUP
        ↓ Price + ↑ OI  -> SHORT_BUILDUP
        ↑ Price + ↓ OI  -> SHORT_COVERING
        ↓ Price + ↓ OI  -> LONG_UNWINDING

    NOTE:
    Version-1 uses snapshot data only.
    Future Version-2 can use ΔPrice and ΔOI between snapshots.
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

    def _classify(self, price: float, oi: float) -> str:
        """
        Snapshot-based classification.
        (Existing logic preserved)
        """

        if price == 0 and oi == 0:
            return "UNKNOWN"

        if price > 0 and oi > 0:
            return "LONG_BUILDUP"

        elif price <= 0 and oi > 0:
            return "SHORT_BUILDUP"

        elif price > 0 and oi <= 0:
            return "SHORT_COVERING"

        return "LONG_UNWINDING"

    def _count_flow(self, series: pd.Series) -> dict:
        """
        Count occurrences of every flow type.
        """

        counts = {}

        for flow in self.FLOW_TYPES:
            counts[flow.lower()] = int((series == flow).sum())

        return counts

    def _market_bias(self, ce_summary: dict, pe_summary: dict) -> str:

        call_long = ce_summary["long_buildup"]
        put_long = pe_summary["long_buildup"]

        if put_long > call_long:
            return "BULLISH"

        if call_long > put_long:
            return "BEARISH"

        return "NEUTRAL"

    def _trend(self, ce_summary: dict, pe_summary: dict) -> str:

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

    def analyze(self, greeks_df: pd.DataFrame):

        if greeks_df is None or greeks_df.empty:

            return {
                "summary": {},
                "table": greeks_df,
            }

        df = greeks_df.copy()

        required = [
            "CE_LTP",
            "CE_OI",
            "PE_LTP",
            "PE_OI",
        ]

        for col in required:

            if col not in df.columns:
                df[col] = 0

            df[col] = (
                pd.to_numeric(
                    df[col],
                    errors="coerce",
                )
                .fillna(0)
            )

        # -------------------------------------------------
        # CE Flow
        # -------------------------------------------------

        df["CE_FLOW"] = df.apply(
            lambda row: self._classify(
                float(row["CE_LTP"]),
                float(row["CE_OI"]),
            ),
            axis=1,
        )

        # -------------------------------------------------
        # PE Flow
        # -------------------------------------------------

        df["PE_FLOW"] = df.apply(
            lambda row: self._classify(
                float(row["PE_LTP"]),
                float(row["PE_OI"]),
            ),
            axis=1,
        )

        # -------------------------------------------------
        # Summary
        # -------------------------------------------------

        ce_summary = self._count_flow(df["CE_FLOW"])
        pe_summary = self._count_flow(df["PE_FLOW"])

        summary = {
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