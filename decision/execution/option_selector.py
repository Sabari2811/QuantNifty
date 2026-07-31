from decision.option_contract import OptionContract
from decision.constants import OptionType


class OptionSelector:
    """
    Selects the nearest option contract from the
    live Greeks dataframe.

    Expected dataframe format:

        Strike
        CE_LTP
        CE_OI
        CE_IV
        CE_DELTA
        ...

        PE_LTP
        PE_OI
        PE_IV
        PE_DELTA
        ...
    """

    def select(self, snapshot, strike, option_type):

        df = snapshot.greeks_df

        # --------------------------------------------------
        # Validate dataframe
        # --------------------------------------------------

        if df is None or df.empty:
            return None

        option_type = option_type.upper()

        if option_type not in (
            OptionType.CE.value,
            OptionType.PE.value,
        ):
            return None

        # --------------------------------------------------
        # Find nearest strike
        # --------------------------------------------------

        work = df.copy()

        work["distance"] = (
            work["Strike"] - strike
        ).abs()

        row = work.sort_values(
            "distance"
        ).iloc[0]

        strike = int(row["Strike"])

        # ==================================================
        # CE CONTRACT
        # ==================================================

        if option_type == OptionType.CE.value:

            return OptionContract(

                strike=strike,

                option_type="CE",

                expiry=str(row.get("Expiry", "")),

                ltp=float(row.get("CE_LTP", 0)),

                bid=float(row.get("CE_BID", 0)),

                ask=float(row.get("CE_ASK", 0)),

                volume=int(row.get("CE_VOLUME", 0)),

                oi=int(row.get("CE_OI", 0)),

                iv=float(row.get("CE_IV", 0)),

                delta=float(row.get("CE_DELTA", 0)),

                gamma=float(row.get("CE_GAMMA", 0)),

                theta=float(row.get("CE_THETA", 0)),

                vega=float(row.get("CE_VEGA", 0))
            )

        # ==================================================
        # PE CONTRACT
        # ==================================================

        return OptionContract(

            strike=strike,

            option_type="PE",

            expiry=str(row.get("Expiry", "")),

            ltp=float(row.get("PE_LTP", 0)),

            bid=float(row.get("PE_BID", 0)),

            ask=float(row.get("PE_ASK", 0)),

            volume=int(row.get("PE_VOLUME", 0)),

            oi=int(row.get("PE_OI", 0)),

            iv=float(row.get("PE_IV", 0)),

            delta=float(row.get("PE_DELTA", 0)),

            gamma=float(row.get("PE_GAMMA", 0)),

            theta=float(row.get("PE_THETA", 0)),

            vega=float(row.get("PE_VEGA", 0))
        )