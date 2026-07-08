import pandas as pd


class OIFlowEngine:
    """
    Institutional Open Interest Flow Engine

    Classification:

    ↑ Price + ↑ OI  -> Long Build-up
    ↓ Price + ↑ OI  -> Short Build-up
    ↑ Price + ↓ OI  -> Short Covering
    ↓ Price + ↓ OI  -> Long Unwinding
    """

    def __init__(self):
        pass

    def analyze(self, greeks_df: pd.DataFrame):

        if greeks_df.empty:
            return greeks_df

        df = greeks_df.copy()

        # ---------------------------------------
        # CE Analysis
        # ---------------------------------------

        ce_flow = []

        for _, row in df.iterrows():

            price = row["CE_LTP"]
            oi = row["CE_OI"]

            if price > 0 and oi > 0:
                ce_flow.append("LONG_BUILDUP")

            elif price <= 0 and oi > 0:
                ce_flow.append("SHORT_BUILDUP")

            elif price > 0 and oi <= 0:
                ce_flow.append("SHORT_COVERING")

            else:
                ce_flow.append("LONG_UNWINDING")

        df["CE_FLOW"] = ce_flow

        # ---------------------------------------
        # PE Analysis
        # ---------------------------------------

        pe_flow = []

        for _, row in df.iterrows():

            price = row["PE_LTP"]
            oi = row["PE_OI"]

            if price > 0 and oi > 0:
                pe_flow.append("LONG_BUILDUP")

            elif price <= 0 and oi > 0:
                pe_flow.append("SHORT_BUILDUP")

            elif price > 0 and oi <= 0:
                pe_flow.append("SHORT_COVERING")

            else:
                pe_flow.append("LONG_UNWINDING")

        df["PE_FLOW"] = pe_flow

        return df