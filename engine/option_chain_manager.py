import pandas as pd


class OptionChainManager:

    def __init__(
        self,
        provider,
        strike_selector,
        instrument_manager,
        market_manager
    ):

        self.provider = provider
        self.selector = strike_selector
        self.instrument_manager = instrument_manager
        self.market = market_manager

    # -------------------------------------------------------
    # Live Option Chain
    # -------------------------------------------------------

    def get_live_option_chain(
        self,
        symbol,
        spot_price,
        levels=5
    ):

        expiry = self.instrument_manager.get_nearest_weekly_expiry(
            symbol
        )

        contracts = self.selector.get_option_security_ids(
            symbol=symbol,
            expiry=expiry,
            spot_price=spot_price,
            levels=levels
        )

        if not contracts:
            raise Exception(
                "No option contracts found for selected expiry."
            )

        security_ids = []

        for c in contracts:

            security_ids.append(c["CE_ID"])
            security_ids.append(c["PE_ID"])

        print()
        print("=" * 70)
        print("OPTION CONTRACTS")
        print("=" * 70)

        for c in contracts:

            print(
                f"{c['strike']}  CE:{c['CE_ID']}  PE:{c['PE_ID']}"
            )

        quotes = self.provider.get_quotes(security_ids)

        rows = []

        for contract in contracts:

            ce_key = f"NFO_{contract['CE_ID']}"
            pe_key = f"NFO_{contract['PE_ID']}"

            ce = quotes.get(ce_key, {})
            pe = quotes.get(pe_key, {})

            rows.append({

                "Strike": contract["strike"],

                "CE_ID": contract["CE_ID"],
                "CE_LTP": ce.get("live_price"),
                "CE_OI": ce.get("open_interest"),
                "CE_VOLUME": ce.get("volume"),

                "PE_ID": contract["PE_ID"],
                "PE_LTP": pe.get("live_price"),
                "PE_OI": pe.get("open_interest"),
                "PE_VOLUME": pe.get("volume")

            })

        df = pd.DataFrame(rows)

        return df