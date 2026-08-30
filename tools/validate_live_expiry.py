"""Validate NIFTY expiry selection against a freshly downloaded F&O master."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.instrument_manager import InstrumentManager


def _parse_provider_expiry(value) -> datetime:
    """Normalize provider expiry strings used by the F&O master."""
    text = str(value).strip()
    formats = (
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    # Final fallback for values parseable by pandas without silently accepting
    # an unparseable contract date.
    try:
        import pandas as pd
        parsed = pd.to_datetime(text, errors="raise")
        return parsed.to_pydatetime()
    except Exception as exc:
        raise RuntimeError(f"Unable to parse selected expiry {value}") from exc


def validate(symbol: str = "NIFTY") -> dict:
    manager = InstrumentManager()
    manager.download_instruments("fno")
    expiry = manager.get_nearest_weekly_expiry(symbol)
    options = manager.get_options(symbol)

    if expiry is None:
        raise RuntimeError(f"No future weekly expiry found for {symbol} after F&O master refresh")

    selected = options[options["EXPIRY_DATE"].astype(str) == str(expiry)].copy()
    if selected.empty:
        raise RuntimeError(f"Selected expiry {expiry} is absent from refreshed {symbol} option master")

    flags = selected["EXPIRY_FLAG"].astype(str).str.upper().unique().tolist()
    if "W" not in flags:
        raise RuntimeError(f"Selected expiry {expiry} is not marked weekly in refreshed {symbol} master")

    expiry_dt = _parse_provider_expiry(selected["EXPIRY_DATE"].iloc[0])
    if expiry_dt.date() <= datetime.now().date():
        raise RuntimeError(f"Selected expiry {expiry} is not future-dated")

    return {
        "validated_at_local": datetime.now().isoformat(),
        "symbol": symbol,
        "expiry": str(expiry),
        "expiry_flag": "W",
        "matching_contract_rows": int(len(selected)),
        "master_refreshed": True,
        "parsed_expiry": expiry_dt.isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="NIFTY")
    args = parser.parse_args()
    result = validate(args.symbol)
    print(json.dumps(result, indent=2))
    print("LIVE_EXPIRY_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
