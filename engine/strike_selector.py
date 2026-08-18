class StrikeSelector:

    def __init__(self, instrument_manager):
        self.instrument_manager = instrument_manager

    # -------------------------------------------------------
    # ATM Strike
    # -------------------------------------------------------

    def get_atm_strike(self, spot_price):

        return int(round(float(spot_price) / 50) * 50)

    # -------------------------------------------------------
    # Strike Range
    # -------------------------------------------------------

    def get_surrounding_strikes(
        self,
        spot_price,
        levels=5,
        step=50
    ):

        atm = self.get_atm_strike(spot_price)

        return [
            atm + (i * step)
            for i in range(-levels, levels + 1)
        ]

    # -------------------------------------------------------
    # Option Contracts
    # -------------------------------------------------------

    def get_option_security_ids(
        self,
        symbol,
        expiry,
        spot_price,
        levels=5
    ):

        if not expiry:
            return []

        strikes = self.get_surrounding_strikes(
            spot_price,
            levels
        )

        contracts = []

        for strike in strikes:

            ce = self.instrument_manager.get_option(
                symbol=symbol,
                expiry=expiry,
                strike=float(strike),
                option_type="CE"
            )

            pe = self.instrument_manager.get_option(
                symbol=symbol,
                expiry=expiry,
                strike=float(strike),
                option_type="PE"
            )

            if ce is None:
                print(f"Missing CE : {strike}")

            if pe is None:
                print(f"Missing PE : {strike}")

            if ce is None or pe is None:
                continue

            contracts.append({
                "strike": strike,
                "CE_ID": int(ce["SECURITY_ID"]),
                "PE_ID": int(pe["SECURITY_ID"])
            })

        return contracts

