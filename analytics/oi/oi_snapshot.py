from datetime import datetime


class OISnapshot:
    """
    Stores an option chain snapshot.
    Compatible with QuantNifty OptionChainManager.
    """

    def __init__(self):

        self.timestamp = datetime.now()

        self.data = {}

    def save(self, option_chain):

        self.timestamp = datetime.now()

        self.data = {}

        for _, row in option_chain.iterrows():

            strike = float(row["Strike"])

            self.data[strike] = {

                "ce_oi": float(row["CE_OI"]),

                "pe_oi": float(row["PE_OI"]),

                "ce_volume": float(row["CE_VOLUME"]),

                "pe_volume": float(row["PE_VOLUME"])

            }

        return self

    def get(self):

        return self.data