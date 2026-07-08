from utils.cache import LookupCache


class LookupBuilder:
    """
    Builds high-performance lookup caches from
    instrument master DataFrames.
    """

    def __init__(self):

        self.option_lookup = LookupCache()
        self.expiry_lookup = LookupCache()
        self.lot_lookup = LookupCache()
        self.index_lookup = LookupCache()

    # ----------------------------------------------------
    # OPTION LOOKUP
    # ----------------------------------------------------

    def build_option_lookup(self, df):

        self.option_lookup.clear()

        for _, row in df.iterrows():

            symbol = (
                str(row["TRADING_SYMBOL"])
                .split("-")[0]
                .upper()
            )

            key = (
                symbol,
                row["EXPIRY_DATE"],
                float(row["STRIKE_PRICE"]),
                row["OPTION_TYPE"].upper()
            )

            self.option_lookup.add(key, row)

        return self.option_lookup.size()

    # ----------------------------------------------------
    # EXPIRY LOOKUP
    # ----------------------------------------------------

    def build_expiry_lookup(self, df):

        self.expiry_lookup.clear()

        symbols = (
            df["TRADING_SYMBOL"]
            .str.split("-")
            .str[0]
            .unique()
        )

        for symbol in symbols:

            expiry = (
                df[
                    df["TRADING_SYMBOL"]
                    .str.startswith(symbol)
                ]["EXPIRY_DATE"]
                .drop_duplicates()
                .sort_values()
                .tolist()
            )

            self.expiry_lookup.add(symbol, expiry)

        return self.expiry_lookup.size()

    # ----------------------------------------------------
    # LOT SIZE LOOKUP
    # ----------------------------------------------------

    def build_lot_lookup(self, df):

        self.lot_lookup.clear()

        symbols = (
            df["TRADING_SYMBOL"]
            .str.split("-")
            .str[0]
            .unique()
        )

        for symbol in symbols:

            lot = int(
                df[
                    df["TRADING_SYMBOL"]
                    .str.startswith(symbol)
                ]
                .iloc[0]["LOT_UNITS"]
            )

            self.lot_lookup.add(symbol, lot)

        return self.lot_lookup.size()

    # ----------------------------------------------------
    # INDEX LOOKUP
    # ----------------------------------------------------

    def build_index_lookup(self, df):

        self.index_lookup.clear()

        for _, row in df.iterrows():

            self.index_lookup.add(
                row["SEGMENT"].upper(),
                int(row["SECURITY_ID"])
            )

        return self.index_lookup.size()