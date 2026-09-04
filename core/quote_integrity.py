from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Literal

import pandas as pd


IntegrityStatus = Literal["VALID", "SUSPECT", "INVALID"]


@dataclass(frozen=True, slots=True)
class QuoteIntegrityReport:
    """Deterministic structural/pricing checks for a live option chain.

    The validator never changes the raw quotes. A below-intrinsic LTP is
    classified as SUSPECT rather than INVALID because an LTP can be a stale
    last trade while the underlying has moved. A provider timestamp does not
    by itself clear that finding because the INDstocks documentation does not
    define the full-quote timestamp as the observation timestamp of the LTP.
    """

    status: IntegrityStatus
    checked_contracts: int = 0
    valid_contracts: int = 0
    suspect_contracts: int = 0
    invalid_contracts: int = 0
    reasons: tuple[str, ...] = ()
    contract_reasons: tuple[tuple[str, tuple[str, ...]], ...] = ()

    @property
    def usable_for_analytics(self) -> bool:
        """Whether the chain has no structural integrity failures."""
        return self.status != "INVALID"

    def as_dict(self) -> dict:
        return asdict(self)


def _finite_float(value):
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _contract_id_text(value) -> str:
    """Render numeric contract IDs canonically, avoiding pandas float suffixes."""
    numeric = _finite_float(value)
    if numeric is not None and numeric.is_integer():
        return str(int(numeric))
    return str(value)


def _contract_key(row, row_number: int) -> str:
    """Return a stable human/reconciliation key for an option contract row."""
    strike = _finite_float(row.get("Strike"))
    strike_text = str(int(strike)) if strike is not None and strike.is_integer() else str(strike)
    ce_id = _contract_id_text(row.get("CE_ID"))
    pe_id = _contract_id_text(row.get("PE_ID"))
    return f"strike:{strike_text}|CE:{ce_id}|PE:{pe_id}|row:{row_number}"


def assess_option_chain(
    option_chain: pd.DataFrame,
    spot_price: float,
    *,
    intrinsic_tolerance: float = 0.01,
) -> QuoteIntegrityReport:
    """Assess option-chain integrity without mutating the input DataFrame.

    Checks include:
    - valid positive spot/strike values
    - presence of contract identifiers
    - finite, non-negative LTP/OI/volume values
    - LTP below spot-based intrinsic value

    A below-intrinsic LTP is only a SUSPECT condition. This deliberately
    avoids treating a potentially stale last trade as fabricated data. The
    finding remains SUSPECT even when a provider timestamp is available,
    unless a provider contract explicitly establishes that the timestamp
    describes the LTP observation itself.
    """

    if not isinstance(option_chain, pd.DataFrame) or option_chain.empty:
        return QuoteIntegrityReport(
            status="INVALID",
            reasons=("option_chain_empty",),
        )

    spot = _finite_float(spot_price)
    if spot is None or spot <= 0:
        return QuoteIntegrityReport(
            status="INVALID",
            checked_contracts=len(option_chain),
            invalid_contracts=len(option_chain),
            reasons=("invalid_spot_price",),
        )

    required_columns = {
        "Strike",
        "CE_ID",
        "CE_LTP",
        "CE_OI",
        "CE_VOLUME",
        "PE_ID",
        "PE_LTP",
        "PE_OI",
        "PE_VOLUME",
    }
    missing_columns = tuple(
        sorted(required_columns.difference(option_chain.columns))
    )
    if missing_columns:
        return QuoteIntegrityReport(
            status="INVALID",
            checked_contracts=len(option_chain),
            invalid_contracts=len(option_chain),
            reasons=(f"missing_columns:{','.join(missing_columns)}",),
        )

    reasons: list[str] = []
    contract_reasons: list[tuple[str, tuple[str, ...]]] = []
    valid_count = 0
    suspect_count = 0
    invalid_count = 0

    for row_number, row in option_chain.reset_index(drop=True).iterrows():
        strike = _finite_float(row["Strike"])
        row_reasons: list[str] = []
        row_suspect = False
        row_invalid = False

        if strike is None or strike <= 0:
            row_reasons.append("invalid_strike")
            row_invalid = True

        for option_type in ("CE", "PE"):
            contract_id = row[f"{option_type}_ID"]
            if contract_id is None or (isinstance(contract_id, float) and math.isnan(contract_id)):
                row_reasons.append(f"missing_{option_type.lower()}_id")
                row_invalid = True

            ltp = _finite_float(row[f"{option_type}_LTP"])
            if ltp is None:
                row_reasons.append(f"missing_{option_type.lower()}_ltp")
                row_invalid = True
            elif ltp < 0:
                row_reasons.append(f"negative_{option_type.lower()}_ltp")
                row_invalid = True
            elif strike is not None:
                intrinsic = (
                    max(spot - strike, 0.0)
                    if option_type == "CE"
                    else max(strike - spot, 0.0)
                )
                if ltp + intrinsic_tolerance < intrinsic:
                    row_reasons.append(
                        f"{option_type.lower()}_ltp_below_intrinsic"
                    )
                    row_suspect = True

            for field_name in ("OI", "VOLUME"):
                value = _finite_float(row[f"{option_type}_{field_name}"])
                if value is None:
                    row_reasons.append(
                        f"missing_{option_type.lower()}_{field_name.lower()}"
                    )
                    row_invalid = True
                elif value < 0:
                    row_reasons.append(
                        f"negative_{option_type.lower()}_{field_name.lower()}"
                    )
                    row_invalid = True

        if row_reasons:
            contract_reasons.append(
                (_contract_key(row, row_number), tuple(row_reasons))
            )
            reasons.extend(row_reasons)

        if row_invalid:
            invalid_count += 1
        elif row_suspect:
            suspect_count += 1
        else:
            valid_count += 1

    unique_reasons = tuple(dict.fromkeys(reasons))

    if invalid_count:
        status: IntegrityStatus = "INVALID"
    elif suspect_count:
        status = "SUSPECT"
    else:
        status = "VALID"

    return QuoteIntegrityReport(
        status=status,
        checked_contracts=len(option_chain),
        valid_contracts=valid_count,
        suspect_contracts=suspect_count,
        invalid_contracts=invalid_count,
        reasons=unique_reasons,
        contract_reasons=tuple(contract_reasons),
    )
