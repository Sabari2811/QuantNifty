from decision.option_contract import OptionContract
from decision.constants import OptionType


class OptionSelector:
    """
    Selects the nearest option contract from the
    live Greeks dataframe.

    Missing/unusable Greek values are not converted to zero. A contract
    requiring Greeks is rejected when its required Greek is unavailable,
    rather than silently creating a misleading trade contract.
    """

    _GREEK_FIELDS = {
        OptionType.CE.value: ("CE_IV", "CE_DELTA", "CE_GAMMA", "CE_THETA", "CE_VEGA"),
        OptionType.PE.value: ("PE_IV", "PE_DELTA", "PE_GAMMA", "PE_THETA", "PE_VEGA"),
    }

    def select(self, snapshot, strike, option_type):
        df = snapshot.greeks_df

        if df is None or df.empty:
            return None

        option_type = option_type.upper()

        if option_type not in (OptionType.CE.value, OptionType.PE.value):
            return None

        work = df.copy()
        work["distance"] = (work["Strike"] - strike).abs()
        row = work.sort_values("distance").iloc[0]

        fields = self._GREEK_FIELDS[option_type]
        if any(row.get(field) is None for field in fields):
            return None

        strike = int(row["Strike"])

        prefix = option_type
        return OptionContract(
            strike=strike,
            option_type=option_type,
            expiry=str(row.get("Expiry", "")),
            ltp=float(row.get(f"{prefix}_LTP", 0) or 0),
            bid=float(row.get(f"{prefix}_BID", 0) or 0),
            ask=float(row.get(f"{prefix}_ASK", 0) or 0),
            volume=int(row.get(f"{prefix}_VOLUME", 0) or 0),
            oi=int(row.get(f"{prefix}_OI", 0) or 0),
            iv=float(row[f"{prefix}_IV"]),
            delta=float(row[f"{prefix}_DELTA"]),
            gamma=float(row[f"{prefix}_GAMMA"]),
            theta=float(row[f"{prefix}_THETA"]),
            vega=float(row[f"{prefix}_VEGA"]),
        )
