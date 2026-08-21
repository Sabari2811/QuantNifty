from __future__ import annotations

from analytics.intelligence.extractors.base_extractor import BaseExtractor


class GreeksExtractor(BaseExtractor):
    """
    Extracts Greeks and option-contract statistics for the
    selected trade contract.

    This extractor performs field mapping only.

    It does NOT:
        - calculate Greeks
        - calculate IV rank
        - calculate IV percentile
        - select a different strike
        - make a trading decision
    """

    def extract(
        self,
        ctx,
        record,
    ) -> None:

        greeks_df = getattr(
            ctx,
            "greeks_df",
            None,
        )

        if greeks_df is None:
            return

        if getattr(greeks_df, "empty", True):
            return

        decision = getattr(
            ctx,
            "decision",
            None,
        )

        if decision is None:
            return

        trade = getattr(
            decision,
            "trade",
            None,
        )

        if trade is None:
            return

        strike = getattr(
            trade,
            "strike",
            None,
        )

        option_type = str(
            getattr(
                trade,
                "option_type",
                "",
            )
            or ""
        ).upper()

        if strike is None:
            return

        if option_type not in ("CE", "PE"):
            return

        #
        # Find selected strike
        #

        try:
            rows = greeks_df[
                greeks_df["Strike"] == strike
            ]
        except (KeyError, TypeError):
            return

        if rows.empty:
            return

        row = rows.iloc[0]

        prefix = option_type

        def value(
            column: str,
            default=0.0,
        ):
            try:
                result = row[column]

            except (KeyError, TypeError):
                return default

            if result is None:
                return default

            return result

        #
        # Selected contract
        #

        record.strike = value(
            "Strike",
            strike,
        )

        record.option_type = option_type

        #
        # Greeks
        #

        record.implied_volatility = value(
            f"{prefix}_IV",
        )

        record.delta = value(
            f"{prefix}_DELTA",
        )

        record.gamma = value(
            f"{prefix}_GAMMA",
        )

        record.theta = value(
            f"{prefix}_THETA",
        )

        record.vega = value(
            f"{prefix}_VEGA",
        )

        record.rho = value(
            f"{prefix}_RHO",
        )

        #
        # Option-chain statistics
        #

        record.open_interest = value(
            f"{prefix}_OI",
        )

        record.change_in_oi = value(
            f"{prefix}_OI_CHANGE",
        )

        record.volume = value(
            f"{prefix}_VOLUME",
        )

        #
        # Intentionally NOT populated here:
        #
        # premium
        # iv_rank
        # iv_percentile
        #
        # Their authoritative source has not been established
        # by the current repository contract.
