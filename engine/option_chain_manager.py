from datetime import datetime, timezone

import pandas as pd

from core.data_provenance import AcquisitionProvenance


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

        if not expiry:
            raise Exception(
                "No future option expiry found."
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

        for contract in contracts:

            security_ids.append(
                contract["CE_ID"]
            )

            security_ids.append(
                contract["PE_ID"]
            )

        print()
        print("=" * 70)
        print("OPTION EXPIRY")
        print("=" * 70)
        print(expiry)

        print()
        print("=" * 70)
        print("OPTION CONTRACTS")
        print("=" * 70)

        for contract in contracts:

            print(
                f"{contract['strike']}  "
                f"CE:{contract['CE_ID']}  "
                f"PE:{contract['PE_ID']}"
            )

        # ---------------------------------------------------
        # Fetch live quotes
        # ---------------------------------------------------

        acquired_at = datetime.now(timezone.utc)

        quotes = self.provider.get_quotes(
            security_ids
        )

        missing_ids = {
            security_id
            for security_id in security_ids
            if f"NFO_{security_id}" not in quotes
        }

        provenance = AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=acquired_at,
            expected_count=len(security_ids),
            received_count=len(security_ids) - len(missing_ids),
            missing_count=len(missing_ids),
            freshness_verified=False,
            reasons=(
                ("provider_quote_timestamp_unavailable",)
                if quotes
                else ("no_option_quotes_received",)
            ),
        )

        rows = []

        for contract in contracts:

            ce_key = (
                f"NFO_{contract['CE_ID']}"
            )

            pe_key = (
                f"NFO_{contract['PE_ID']}"
            )

            ce = quotes.get(
                ce_key,
                {}
            )

            pe = quotes.get(
                pe_key,
                {}
            )

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

        result = pd.DataFrame(rows)
        result.attrs["data_provenance"] = provenance

        return result