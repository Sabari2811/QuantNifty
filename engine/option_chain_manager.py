from datetime import datetime, timezone

import pandas as pd

from core.data_provenance import AcquisitionProvenance
from core.quote_integrity import assess_option_chain


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

        # Coverage is measured against the contract universe requested by
        # the runtime, not only the contracts that happened to exist in the
        # local instrument master.  This prevents a missing instrument from
        # disappearing from the denominator and producing false 100% coverage.
        requested_strikes = (2 * int(levels)) + 1
        expected_contract_count = requested_strikes * 2
        instrument_contract_count = len(contracts) * 2
        missing_instrument_count = max(
            0,
            expected_contract_count - instrument_contract_count,
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

        # ---------------------------------------------------
        # Quote integrity
        # ---------------------------------------------------
        # Do not alter or clamp provider values.  The report is an
        # observation layer that travels with the raw chain.
        integrity = assess_option_chain(
            result,
            spot_price,
        )

        provenance_reasons = []
        if quotes:
            provenance_reasons.append(
                "provider_quote_timestamp_unavailable"
            )
        else:
            provenance_reasons.append(
                "no_option_quotes_received"
            )
        if missing_instrument_count:
            provenance_reasons.append(
                f"missing_instrument_contracts:{missing_instrument_count}"
            )
        if missing_ids:
            provenance_reasons.append(
                f"missing_provider_quotes:{len(missing_ids)}"
            )

        received_count = len(security_ids) - len(missing_ids)
        missing_count = expected_contract_count - received_count

        provenance = AcquisitionProvenance(
            source="INDMoney option quotes",
            acquired_at=acquired_at,
            expected_count=expected_contract_count,
            received_count=received_count,
            missing_count=missing_count,
            freshness_verified=False,
            reasons=tuple(provenance_reasons),
            integrity_status=integrity.status,
            integrity_reasons=integrity.reasons,
        )

        result.attrs["data_provenance"] = provenance
        result.attrs["quote_integrity"] = integrity.as_dict()

        return result
