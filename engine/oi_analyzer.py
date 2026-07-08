class OIAnalyzer:

    def analyze(self, df):

        total_call_oi = df["CE_OI"].sum()
        total_put_oi = df["PE_OI"].sum()

        pcr = round(
            total_put_oi / total_call_oi,
            2
        ) if total_call_oi else 0

        max_call_row = df.loc[df["CE_OI"].idxmax()]
        max_put_row = df.loc[df["PE_OI"].idxmax()]

        resistance = max_call_row["Strike"]
        support = max_put_row["Strike"]

        call_oi = max_call_row["CE_OI"]
        put_oi = max_put_row["PE_OI"]

        if pcr > 1.15:
            bias = "Bullish"

        elif pcr < 0.85:
            bias = "Bearish"

        else:
            bias = "Sideways"

        return {

            "Total Call OI": int(total_call_oi),

            "Total Put OI": int(total_put_oi),

            "PCR": pcr,

            "Support": support,

            "Resistance": resistance,

            "Max Put OI": int(put_oi),

            "Max Call OI": int(call_oi),

            "Market Bias": bias

        }